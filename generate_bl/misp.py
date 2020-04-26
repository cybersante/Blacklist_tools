#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create ipset from MISP
# Author: Lionel PRAT
# Code modified from: https://github.com/MISP/PyMISP/blob/master/examples/last.py
 
from pymisp import ExpandedPyMISP
from keys import misp_url, misp_key, misp_verifycert
try:
    from keys import misp_client_cert
except ImportError:
    misp_client_cert = ''
import argparse
import os
import json
import re
import datetime
# Usage for pipe masters: ./last.py -l 5h | jq .
# Usage in case of large data set and pivoting page by page: python3 last.py  -l 48h  -m 10 -p 2  | jq .[].Event.info

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download latest events from a MISP instance.')
    parser.add_argument("-l", "--last", required=True, help="can be defined in days, hours, minutes (for example 5d or 12h or 30m).")
    parser.add_argument("-o", "--output", help="Output file")

    args = parser.parse_args()

    if misp_client_cert == '':
        misp_client_cert = None
    else:
        misp_client_cert = (misp_client_cert)
    x=datetime.date.today() -  datetime.timedelta(days=45)
    misp = ExpandedPyMISP(misp_url, misp_key, misp_verifycert, cert=misp_client_cert)
    #result = misp.search(publish_timestamp=args.last, limit=args.limit, page=args.page, pythonify=True)
    result = misp.search(controller='attributes', timestamp=args.last, type_attribute=['ip-src','ip-dst'], to_ids='1', pythonify=True)
    if not result:
        print('No results for that time period')
        exit(0)
    ipbl=[]
    regex1 = re.compile(r'\d+\.\d+\.\d+\.\d+')
    regex2 = re.compile(r'(127\.[0-9]+\.[0-9]+\.[0-9]+|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.([1-2][0-9]|0|30|31)\.\d+\.\d+|255\.255\.255\.\d+)')
    if args.output:
        with open(args.output, 'w') as f:
            for elemx in result:
                #print('Elemx:'+str(elemx))
                if 'ip' in elemx['type']:
                    tmpx=re.sub('\|\d+','',elemx['value'])
                    if regex1.match(tmpx) and not regex2.match(tmpx) and tmpx not in ipbl:
                        ipbl.append(tmpx)
                        f.write(str(tmpx)+"\n")
