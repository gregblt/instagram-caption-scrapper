#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 17:56:23 2018

@author: gregory
"""

from selenium import webdriver
import requests
from bs4 import BeautifulSoup
#driver = webdriver.Firefox()
import json
import shutil
import os

#driver.find_elements_by_class_name("Y8-fY")[1].click()
username="natoogram"

r=requests.get('https://www.instagram.com/'+username)
if(r.status_code==200):
	soup=BeautifulSoup(r.content,'lxml')
		# with open('lol.html','w') as f:
		# 	f.write(str(soup))
			
	objects = json.loads(str(soup).split('<script type="text/javascript">window._sharedData = ')[1].split(';</script>')[0])['entry_data']['ProfilePage'][0]['graphql']['user']
		# Get followers count
	followers_count=objects['edge_followed_by']['count']
    
headers={   
    "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8'
}
url="https://www.instagram.com/graphql/query/?query_hash=56066f031e6239f35a904ac20c9f37d9&variables=%7B%22id%22%3A%228630260%22%2C%22include_reel%22%3Atrue%2C%22fetch_mutual%22%3Afalse%2C%22first%22%3A24%7D"
r=requests.get(url,headers=headers)
print(r)

folder_image_location="./outputs/"+username+"/images/"
folder_video_location="./outputs/"+username+"/videos/"
folder_gallery_location="./outputs/"+username+"/galleries/"

post_link="https://www.instagram.com/p/BmywbeIDSSh/?hl=fr&taken-by=natoogram"
#post_link="https://www.instagram.com/p/Bm0qI7KDyVS/?hl=fr&taken-by=natoogram"
post_link="https://www.instagram.com/p/Bmtvo89DZzX/?hl=fr&taken-by=natoogram"
r=requests.get(post_link)
if(r.status_code==200):
    
    soup=BeautifulSoup(r.content,'lxml')     			
    objects = json.loads(str(soup).split('<script type="text/javascript">window._sharedData = ')[1].split(';</script>')[0])["entry_data"]["PostPage"][0]["graphql"]['shortcode_media']
    post_type=objects["__typename"]
    media_id=objects["id"]
    nb_ressources=len(objects["display_resources"])
    if(post_type=="GraphVideo"):
        folder_out=folder_video_location
        download_url=[objects["video_url"]]
        media_dim=[str(objects["display_resources"][nb_ressources-1]['config_width']) \
        + "x"+str(objects["display_resources"][nb_ressources-1]['config_height'])]
    elif(post_type=="GraphImage"):
        folder_out=folder_image_location
        download_url=[objects["display_resources"][nb_ressources-1]['src']]
        media_dim=[str(objects["display_resources"][nb_ressources-1]['config_width']) \
        + "x"+str(objects["display_resources"][nb_ressources-1]['config_height'])]
    else:
        download_url=[]
        media_dim=[]
        folder_out=folder_gallery_location+"gallery_"+str(media_id)+"/"
        try:
            os.mkdir(folder_out)
        except:
            pass
        
        for obj in objects["edge_sidecar_to_children"]["edges"]:
            download_url.append(obj['node']["display_resources"][nb_ressources-1]['src'])
            media_dim.append(str(obj['node']["display_resources"][nb_ressources-1]['config_width']) \
            + "x"+str(obj['node']["display_resources"][nb_ressources-1]['config_height']))

    
media_size=[]
import os
for idx,file_uri in enumerate(download_url):
    path=(folder_out+(os.path.basename(file_uri))).split("?")[0]
    r=requests.get(file_uri,headers=headers)
    ans_header=r.headers
    media_size.append(int(ans_header.get('content-length'))/1000)
    if(r.status_code==200):
        with open(path, 'wb') as f:
            f.write(r.content)        