import gzip
import modules.parse_fg_logs
import re

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




def main():

    logtype = 'fortigate'
    logformat = {'srcipfield': 'remip',
                 'datefield': 'date',
                 'timefield': 'time',
                 'protofield': 'proto',
                 'userfield': 'user',
                 'assignIPfield': 'assignip',
                 'statusfield': 'status'
                 }
    parse_fg_logs.get_communication_matrix('../logs_samples/fortigate/fg_user_vpn_sample.log', logformat)
    
    
    # check geoloc
    
