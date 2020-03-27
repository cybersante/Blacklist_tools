#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create backlist IP in JSON format
# Author: Lionel PRAT
import json
import os
import ipaddress

blacklist={}
for root, directories, filenames in os.walk('./blacklist/'):
    for filename in filenames:
        filex=os.path.join(root, filename)
        if filex.endswith(".ipset"):
            with open(filex) as file_in:
                lines = []
                for line in file_in:
                    ipx=line.rstrip()
                    if ipx and not ipx.startswith('#'):
                        if "/" in ipx:
                            #get all ip in cidr
                            ipadd=ipaddress.IPv4Network(ipx)
                            for ipz in ipadd:
                                if ipx not in blacklist:
                                    blacklist[ipx]=[str(filex)]
                                else:
                                    if str(filex) not in blacklist[ipx]:
                                        blacklist[ipx].append(str(filex))
                        else:
                            if ipx not in blacklist:
                                blacklist[ipx]=[str(filex)]
                            else:
                                if str(filex) not in blacklist[ipx]:
                                    blacklist[ipx].append(str(filex))
with open('./result/db-ipbl.json', 'w') as json_file:
    print("Write db-ipbl file")
    json.dump(blacklist, json_file, indent=4, sort_keys=True)  

