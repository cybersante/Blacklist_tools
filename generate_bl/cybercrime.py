#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create ipset from cybercrime web site
# Author: Lionel PRAT
from urllib.parse import urlparse
import requests
import re
import json
import os
import sys
ipbl=[]
import dns.resolver
import dns.reversename
resolver = dns.resolver.Resolver()
resolver.timeout = 3
resolver.lifetime = 1
regex1 = re.compile(r'\d+\.\d+\.\d+\.\d+')
response = requests.get('http://cybercrime-tracker.net/all.php')
if response.status_code == 200:
    with open('./blacklist/cybercrime.ipset', 'w') as f:
        for line in response.text.split('\n'):
            if not line:
                continue
            ret=urlparse('//'+line)
            try:
                ipx=[str(ret.netloc)]
            except:
                continue
            if not regex1.match(str(ret.netloc)):
            #resolv
                #print("Check domain:"+str(ret.netloc))
                ipx=[]
                try:
                    answers_IPv4 = resolver.query(str(ret.netloc), 'A')
                except:
                    continue
                #get IP from domain name
                for rdata in answers_IPv4:
                    if str(rdata.address) not in ipx:
                        ipx.append(str(rdata.address))
            for ip in ipx:
                if ip not in ipbl:
                    ipbl.append(ip)
                    f.write(ip+"\n")
