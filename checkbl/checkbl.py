#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CHECK LOG FILE ON BL & GeoIP - Author: Lionel PRAT
# Version 1.0 - 29/04/2020
# local use
import tempfile
import subprocess
import os
import sys, getopt
import re
import ipaddress
import hashlib
import time
import shutil
import json
import gzip
import modules.parse_fg_logs
from geoip import open_database

#######GLOBAL VAR#######
db=None
databl=None
list_geoip=None
###########################

def get_ip_geoloc(ip):
    global db
    return str(db.lookup(str(ip)).country)


def run_bl_file(filename):
    global databl
    global db 
    global list_geoip
    file_in = None
    retjson={'file_clean':False, 'GeoIP': {}, 'BL': {}}
    try:
        if str(filename).endswith(".gz"):
            #GZIP FILE
            #check ip line by line 
            file_in = gzip.open(filename)
        else:
            file_in = open(filename)
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
                            tmp_ipgeo[ipx] = get_ip_geoloc(ipx)
                            tmp_geo = tmp_ipgeo[ipx]
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
                if find_bl:
                    retjson['lines_suspect'].append({str(cnt): linex,'bl': True, 'geoip':find_geo})
                elif find_geo:
                    retjson['lines_suspect'].append({str(cnt): linex,'bl': False, 'geoip':find_geo})
    except Exception as e:
        retjson['error']=str(e)
    if not 'lines_suspect' in retjson:
        retjson['file_clean']=True
    return retjson


def usage():
    print("Usage: checkbl.py [-r] [-f FR] -b db-ipbl.json -g Geolite2-country.mmdb -p /var/log/ -o badlog.json\n")
    print("\t -h/--help : for help to use\n")
    print("\t -p/--path= : path of filenames to analysis (/var/log/apache2/)\n")
    print("\t -r/--recursive= : Use option recursive to analyze path recursively\n")
    print("\t -f/--filtergeoip= : Filter by GEOIP country code (exemple: FR)\n")
    print("\t -g/--geoipdata= : Path of Geoip Database (Geoip2 lite in mmdb format)\n")
    print("\t -b/--blacklist= : Path of blacklist IP (generated by https://github.com/cybersante/Blacklist_tools/tree/master/generate_bl\n")
    print("\t -o/--output= : file to save result of analyse\n")
    print("\t example: checkbl.py -r -p /var/log/ -g Geolite2-country.mmdb -b db-ipbl.json -o badlog.json\n")


def main(argv):
    print("Check logs with IP BL v1.0")
    global db
    global databl
    global list_geoip
    recursive=False
    pathisfile=False
    path2scan=None
    savefile=None
    try:
        opts, args = getopt.getopt(argv, "hrp:f:g:b:o:", ["help", "recursive", "path=", "filtergeoip=", "geoipdata=", "blacklist=", "output="])
    except getopt.GetoptError:
        usage()
        sys.exit(-1)    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(-1)
        if opt in ("-r", "--recursive"):
            recursive=True
        elif opt in ("-p", "--path"):
            #check if file or path
            if os.path.isdir(arg):
                path2scan=arg
            elif os.path.isfile(arg):
                path2scan=arg
                pathisfile=True
            else:
                print('Error: Path or file '+str(arg)+' not exist.')
                sys.exit()
        elif opt in ("-g", "--geoipdata"):
            #check if file or path
            if os.path.isfile(arg):
                try:
                    db = open_database(arg)
                except Exception as error:
                    print('Error to load: geoip database potentially corrupted => '+str(error))
                    sys.exit()      
            else:
                print('Error: geoip database '+str(arg)+' not exist.')
                sys.exit() 
        elif opt in ("-b", "--blacklist"):
            #check if file or path
            if os.path.isfile(arg):
                try:
                    with open(arg) as json_file:
                        databl = json.load(json_file)
                except Exception as error:
                    print('Error to load: blacklist database => '+str(error))
                    sys.exit()      
            else:
                print('Error: geoip database '+str(arg)+' not exist.')
                sys.exit()   
        elif opt in ("-f", "--filtergeoip"):
            #check if file or path
            if bool(re.search(r'^[A-Za-z,]+$', arg)):
                list_geoip=arg.upper().split(',')
            else:
                print('Error: filter geoip bad format => '+str(arg))
                sys.exit()
        elif opt in ("-o", "--output"):
            #check if file or path
            if not os.path.isfile(arg):
                savefile=arg
            else:
                print('Error: file to save already exist => '+str(arg))
                sys.exit()     
    if savefile and path2scan and databl and db:
        retjson = {}
        if pathisfile:
            print('Analyze file: '+str(path2scan))
            retjson = run_bl_file(path2scan)
        else:
            if recursive:
                for root, directories, filenames in os.walk(path2scan):
                    for filename in filenames:
                        #filename
                        print('Analyze file: '+str(os.path.join(root, filename)))
                        retjson[os.path.join(root, filename)]=run_bl_file(os.path.join(root, filename))
            else:
                for root, directories, filenames in os.walk(path2scan):
                    for filename in filenames:
                        #filename
                        print('Analyze file: '+str(os.path.join(root, filename)))
                        retjson[os.path.join(root, filename)]=run_bl_file(os.path.join(root, filename))
                    break
        print('Analyze finished, save result...')
        with open(savefile, 'w') as json_file:
            json.dump(retjson, json_file, indent=4, sort_keys=True)
    else:
        usage()
        sys.exit(-1)


if __name__ == "__main__":
    main(sys.argv[1:])