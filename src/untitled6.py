#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 18:17:49 2018

@author: gregory
"""

from bs4 import BeautifulSoup
import json, random, re, requests

BASE_URL = 'https://www.instagram.com/accounts/login/'
LOGIN_URL = BASE_URL + 'ajax/'

headers_list = [
        "Mozilla/5.0 (Windows NT 5.1; rv:41.0) Gecko/20100101"\
        " Firefox/41.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2)"\
        " AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2"\
        " Safari/601.3.9",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0)"\
        " Gecko/20100101 Firefox/15.0.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"\
        " (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"\
        " Edge/12.246"
        ]

USERNAME = 'freestagram2018'
PASSWD = 'Freelancer69'
USERNAME = 'gregoleprolo'
PASSWD = 'Mindstorm93'
USERNAME = 'lemaireroro'
PASSWD = 'Freelancer69'
USER_AGENT = headers_list[random.randrange(0,4)]

session = requests.Session()
session.headers = {'user-agent': USER_AGENT}
session.headers.update({'Referer': BASE_URL})    
req = session.get(BASE_URL)    
soup = BeautifulSoup(req.content, 'html.parser')    
body = soup.find('body')

pattern = re.compile('window._sharedData')
script = body.find("script", text=pattern)

script = script.get_text().replace('window._sharedData = ', '')[:-1]
data = json.loads(script)

csrf = data['config'].get('csrf_token')
login_data = {'username': USERNAME, 'password': PASSWD}
session.headers.update({'X-CSRFToken': csrf})
login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
login.content


payload={"query_hash":"56066f031e6239f35a904ac20c9f37d9",
         "variables":json.dumps({"id":"8630260",
                      "include_reel":True,
                      "fetch_mutual":False,
                      "first":50})}

list_prox=['http://27.145.145.161',
           'http://222.106.254.175',
           'http://200.229.195.163'         
        ]

proxies = {
  'http': 'http://64.137.191.20:3128',
  "https": 'http://64.137.191.20:3128'
}


url = 'https://httpbin.org/ip'

response = requests.get(url,proxies=proxies)
print(response.json())

list_u=[]

import time
count=0
url="https://www.instagram.com/graphql/query/"
r=session.get(url,params=payload,proxies=proxies)
data_f=r.json()

list_u+=[u['node']['username'] for u in data_f["data"]["user"]["edge_followed_by"]["edges"]]
count+=len(data_f["data"]["user"]["edge_followed_by"]["edges"])
while(data_f["data"]["user"]["edge_followed_by"]['page_info']['has_next_page']):
    payload={"query_hash":"56066f031e6239f35a904ac20c9f37d9",
             "variables":json.dumps({"id":"8630260",
                          "include_reel":True,
                          "fetch_mutual":False,
                          "first":50,
                          "after":data_f["data"]["user"]["edge_followed_by"]['page_info']['end_cursor']})}    
    url="https://www.instagram.com/graphql/query/"
    r=session.get(url,params=payload)
    data_f=r.json()
    list_u+=[u['node']['username'] for u in data_f["data"]["user"]["edge_followed_by"]["edges"]]
    count+=len(data_f["data"]["user"]["edge_followed_by"]["edges"])
    print(count)
    time.sleep(0.01)
