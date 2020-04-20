#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create ipset from tweettioc web site
# Author: Lionel PRAT
import requests
url = 'http://tweettioc.com/feed/ip'
myfile = requests.get(url)
open('./blacklist/tweettioc.ipset', 'wb').write(myfile.content)
