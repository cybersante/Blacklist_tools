#!flask/bin/python
# API CHECK LOG FILE ON BL & GeoIP - Author: Lionel PRAT
# Version 1.1 - 29/04/2020
# Modified source code origin (thanks):
#  - https://sourcedexter.com/python-rest-api-flask-part-2/
#  - https://github.com/ericsopa/flask-api-key
#  - https://gist.github.com/miguelgrinberg/5614326
#curl -k  -F 'file=@/home/lionel/suspect.log' -F 'geoip=FR' -H "x-api-key: mykeyapi" https://127.0.0.1:8000/api/check_bl_on_log | gzip -d | python -m json.tool > result.json
from flask import Flask, jsonify, abort, request, make_response, url_for, send_file, render_template
#from flask_compress import Compress
from functools import wraps
import tempfile
import subprocess
import os
import re
import ipaddress
import hashlib
import time
import shutil
import json
import gzip
from geoip import open_database

app = Flask(__name__, static_url_path = "")
#Compress(app)
    
def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        with open('api.key', 'r') as apikey:
            key=apikey.read().replace('\n', '')
        #if request.args.get('key') and request.args.get('key') == key:
        if (request.endpoint == 'index') or (request.headers.get('x-api-key') and request.headers.get('x-api-key') == key) or (request.form and  'x-api-key' in request.form and request.form['x-api-key'] and request.form['x-api-key'] == key):
            return view_function(*args, **kwargs)
        else:
            abort(403)
    return decorated_function

@app.errorhandler(403)
def not_found(error):
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(503)
def not_found(error):
    return make_response(jsonify( { 'error': 'Service Unavailable' } ), 503)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

def run_bl_file(file,get_geoip):
    list_geoip=None
    if get_geoip:
        list_geoip=get_geoip.upper().split(',')
    tmpdir = tempfile.mkdtemp()
    retjson={'file_clean':False, 'GeoIP': {}, 'BL': {}}
    with tempfile.NamedTemporaryFile(dir='/tmp', delete=False) as tmpfile:
        temp_file_name = tmpfile.name
        try:
            file.save(temp_file_name)
            #get country file
            databl = None
            db = open_database('/GeoLite2-Country.mmdb')
            with open('/data/db-ipbl.json') as json_file:
                try:
                    databl = json.load(json_file)
                except:
                    abort(503)
            #get BL LIST
            if str(file.filename).endswith(".gz"):
                #GZIP FILE
                #check ip line by line 
                with gzip.open(temp_file_name) as file_in:
                    cnt=0
                    tmp_ipgeo={}
                    for line in file_in:
                        cnt+=1
                        linex=str(line.rstrip())
                        ip = re.findall( r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',linex)
                        find_geo=None
                        find_bl=False
                        for ipx in ip:
                            if not ipaddress.ip_address(str(ipx)).is_private:
                                #Check in BL
                                tmp_geo=None
                                try:
                                    if ipx not in tmp_ipgeo:
                                        tmp_ipgeo[ipx]=str(db.lookup(str(ipx)).country)
                                        tmp_geo=tmp_ipgeo[ipx]
                                    else:
                                        tmp_geo=tmp_ipgeo[ipx]
                                except Exception as error:
                                    print('Error in db lookup on '+str(ipx)+' -> '+str(error))
                                    tmp_geo='Inconnu'
                                if ipx in databl:
                                    find_bl=True
                                    if ipx not in retjson['BL']:
                                        retjson['BL'][ipx]=databl[ipx]
                                    if ipx not in retjson['GeoIP']:
                                        retjson['GeoIP'][ipx]=tmp_geo
                                        find_geo=tmp_geo
                                    else:
                                        find_geo=tmp_geo
                                #Check in GeoIP
                                elif list_geoip and tmp_geo not in list_geoip:
                                    if ipx not in retjson['GeoIP']:
                                        retjson['GeoIP'][ipx]=tmp_geo
                                        find_geo=tmp_geo
                                    else:
                                        find_geo=tmp_geo
                        if find_bl or find_geo:
                            if 'lines_suspect' not in retjson:
                                retjson['lines_suspect']=[]
                                retjson['lines_suspect']=[]
                            if find_bl:
                                retjson['lines_suspect'].append({str(cnt): linex,'bl': True, 'geoip':find_geo})
                            elif find_geo:
                                retjson['lines_suspect'].append({str(cnt): linex,'bl': False, 'geoip':find_geo})
            else:
                #check ip line by line 
                with open(temp_file_name) as file_in:
                    cnt=0
                    tmp_ipgeo={}
                    for line in file_in:
                        cnt+=1
                        linex=str(line.rstrip())
                        ip = re.findall( r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',linex)
                        find_geo=None
                        find_bl=False
                        for ipx in ip:
                            if not ipaddress.ip_address(str(ipx)).is_private:
                                #Check in BL
                                tmp_geo=None
                                try:
                                    if ipx not in tmp_ipgeo:
                                        tmp_ipgeo[ipx]=str(db.lookup(str(ipx)).country)
                                        tmp_geo=tmp_ipgeo[ipx]
                                    else:
                                        tmp_geo=tmp_ipgeo[ipx]
                                except Exception as error:
                                    print('Error in db lookup on '+str(ipx)+' -> '+str(error))
                                    tmp_geo='Inconnu'
                                if ipx in databl:
                                    find_bl=True
                                    if ipx not in retjson['BL']:
                                        retjson['BL'][ipx]=databl[ipx]
                                    if ipx not in retjson['GeoIP']:
                                        retjson['GeoIP'][ipx]=tmp_geo
                                        find_geo=tmp_geo
                                    else:
                                        find_geo=tmp_geo
                                #Check in GeoIP
                                elif list_geoip and tmp_geo not in list_geoip:
                                    if ipx not in retjson['GeoIP']:
                                        retjson['GeoIP'][ipx]=tmp_geo
                                        find_geo=tmp_geo
                                    else:
                                        find_geo=tmp_geo
                        if find_bl or find_geo:
                            if 'lines_suspect' not in retjson:
                                retjson['lines_suspect']=[]
                                retjson['lines_suspect']=[]
                            if find_bl:
                                retjson['lines_suspect'].append({str(cnt): linex,'bl': True, 'geoip':find_geo})
                            elif find_geo:
                                retjson['lines_suspect'].append({str(cnt): linex,'bl': False, 'geoip':find_geo})
                os.remove(temp_file_name)
        except Exception as e:
            print("Error:"+str(e))
            return make_response(jsonify( { 'error': 'Bad file upload' } ), 400)
    if not 'lines_suspect' in retjson:
        retjson['file_clean']=True
    return retjson

@app.route('/', endpoint='index', methods = ['GET'])
@app.route('/api/check_bl_on_log', endpoint='file', methods = ['POST'])
@require_appkey
def upload_file(filename=''):
    if request.endpoint == 'index':
        return render_template('index.html')
    if 'file' not in request.files:
        abort(400)
    get_geoip=None
    #GEOIP='FR,IT,RU' < withlist
    if 'geoip' in request.form and request.form['geoip']:
        if bool(re.search(r'^[A-Za-z,]+$', str(request.form['geoip']))):
            #print("Check geoip:"+str(request.form['geoip']))
            get_geoip=str(request.form['geoip'])
        else:
            abort(400)
    #check db exist:
    if not os.path.isfile('/GeoLite2-Country.mmdb') or not os.path.isfile('/data/db-ipbl.json'):
        abort(503)
    #print request.files
    file = request.files['file']
    retjson = run_bl_file(file,get_geoip)
    #print "retour:"+str(retjson)
    content = gzip.compress(json.dumps(retjson).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response
    #return jsonify( retjson )
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug = True)

