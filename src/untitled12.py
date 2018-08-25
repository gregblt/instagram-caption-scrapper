#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 09:55:32 2018

@author: gregory
"""

import requests
import json
from bs4 import BeautifulSoup

post_link="https://www.instagram.com/p/Bmtvo89DZzX/?taken-by=natoogram"   
r=requests.get(post_link)
if(r.status_code==200):
    soup=BeautifulSoup(r.content,'lxml')     			
    objects = json.loads(str(soup).split('<script type="text/javascript">window._sharedData = ')[1].split(';</script>')[0])["entry_data"]["PostPage"][0]["graphql"]['shortcode_media']
   
comments = objects["edge_media_to_comment"]["count"]