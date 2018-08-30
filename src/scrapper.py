#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 16:16:34 2018

@author: gregory
"""
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import string
import re
import emoji
import sys, traceback
import csv
from selenium.webdriver.firefox.options import Options

# Media size, dim, download
folder_image_location=""
folder_video_location=""
folder_gallery_location=""

def extract_hash_tags(s):
    l = s.split("#")[1:]
    res = []
    for v in l:
        res.append(v.split(" ")[0])
    return res

def get_words(caption):
    # Remove hashtags
    lst=extract_hash_tags(caption)
    if(len(lst)>0):
        lst=[x.lower() for x in lst]
        hashtags=list(set(lst))
        hashtags=sorted(hashtags, key=len, reverse=True)
    for hashtag in hashtags:
        caption=caption.replace("#"+hashtag,"")
    # Remove emojis
    # Emojis
    def extract_emojis(str):
      return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)
    emojis=extract_emojis(caption) 
    for emoji1 in emojis:
        caption=caption.replace(emoji1,"")
    
    # Remove mention
    lst=re.findall(r'@([a-zA-Z0-9._]+)',caption)
    if(len(lst)>0):
        lst=[x.lower() for x in lst]
        mentions=list(set(lst))
        mentions=sorted(mentions, key=len, reverse=True)
    for mention in mentions:
        caption=caption.replace("@"+mention,"")
    
    for c in string.punctuation:
        caption=caption.replace(c,"")
    
    l=[word.lower() for word in caption.lstrip().split()]
    res=[]
    for w in l:
        if ascii(w) != "'\\ufe0f'" :
            res.append(w)
    return res

def add_overall_analysis(list_data,  config):
    
    if(config["hashtags"]):
        hashtags_overall=[data["hashtags"].split(",") for data in list_data]
        
        unique_overall=[]
        for hashtag_list in hashtags_overall:
            unique=[]
            for hashtag in hashtag_list:
                if(sum([hashtag in hashtag_list_t for hashtag_list_t in hashtags_overall])==1):
                    unique.append(hashtag)
            unique_overall.append(unique)
            
        hashtag_uniqueness=[]
        for i in range(0,len(hashtags_overall)):
            if(len(hashtags_overall[i])==0):
                hashtag_uniqueness.append(0)
            else:
                hashtag_uniqueness.append(
                        (len(unique_overall[i]))/(len(hashtags_overall[i]))
                        )
                
        old_hashtags=list_data[len(list_data)-1]["hashtags"].split(",")
        reused_hashtag_count_list=[]
        reused_hashtag_count_list.append(None)
        for data in reversed(list_data[:-1]):
            current_hashtags=data["hashtags"].split(",")
            reused_hashtag_count_list.insert(0,
                                             len([value for value in current_hashtags if value in old_hashtags]))
            old_hashtags=current_hashtags
                
        for idx, data_idx in enumerate(list_data):
            if(config["hashtags"]):
                data_idx["hashtags_unique"]=unique_overall[idx]
                data_idx["hashtags_unique_count"]=len(unique_overall[idx])
                data_idx["hashtag_uniqueness"]=hashtag_uniqueness[idx]
                data_idx["reused_hashtag_count"]=reused_hashtag_count_list[idx]
            else:
                data_idx["hashtags_unique"]=None
                data_idx["hashtags_unique_count"]=None
                data_idx["hashtag_uniqueness"]=None
                data_idx["reused_hashtag_count"]=None
                
    if(config["full_caption"]):
        # Word reused or not
        words_overall=[]
        
        old_words=get_words(list_data[len(list_data)-1]["full_caption"])
        words_overall.append(old_words)
        new_words_count_list=[]
        percent_reused_words_count_list=[]
        new_words_count_list.append(None)
        percent_reused_words_count_list.append(None)
        for data in reversed(list_data[:-1]):
            current_words=get_words(data["full_caption"])
            new_words_count_list.insert(0,
                                             len([value for value in current_words if value not in old_words]))
            nb_reused=len(current_words)-new_words_count_list[0]
            percent_reused_words_count_list.insert(0,nb_reused/len(current_words))
            old_words=current_words
            words_overall.insert(0,old_words)
        
        # Dictionnary uniqueness (overall)old_words=get_words(list_data[len(list_data)-1]["full_caption"])
        word_unique_overall=[]
        for word_list in words_overall:
            word_unique=[]
            for word in word_list:
                if(sum([word_list_t.count(word) for word_list_t in words_overall])==1):
                    word_unique.append(word)
            word_unique_overall.append(word_unique)
            
        dictionnary_uniqueness=[]
        for i in range(0,len(words_overall)):
            if(len(words_overall[i])==0):
                dictionnary_uniqueness.append(0)
            else:
                dictionnary_uniqueness.append(
                        (len(word_unique_overall[i]))/(len(words_overall[i]))
                        )
                
        for idx, data_idx in enumerate(list_data):
            if(config["full_caption"]):
                data_idx["reused_word_percent"]=percent_reused_words_count_list[idx]
                data_idx["new_words_count"]=new_words_count_list[idx]
                data_idx["dictionnary_uniqueness"]=dictionnary_uniqueness[idx]

            else:
                data_idx["reused_word_percent"]=None
                data_idx["new_words_count"]=None
                data_idx["dictionnary_uniqueness"]=None

                
            
    return list_data
    
def create_folder(folder):
    try:
        os.mkdir(folder)
    except:
        pass
    

def scrap_post(post_link,config,driver):    
   
    #driver.get(post_link)
    r=requests.get(post_link)
    if(r.status_code==200):
        soup=BeautifulSoup(r.content,'lxml')     			
        objects = json.loads(str(soup).split('<script type="text/javascript">window._sharedData = ')[1].split(';</script>')[0])["entry_data"]["PostPage"][0]["graphql"]['shortcode_media']
   
    
    # URL
    post_url=None
    if(config["post_link"]):
        post_url = post_link
    

    caption=None
    emojis=None
    number_of_emojis=None
    hashtags=None
    number_of_hashtags=None
    mentions=None
    number_of_mentions=None
    number_of_chars=None
    number_of_words=None
    bounds=[0,10000,20000,50000,100000,200000,500000,2000000,5000000]
    hashtag_rank_list = [[] for i in range(len(bounds))]
    
    if(config["full_caption"] or config["numb_of_char"] or config["numb_of_words"] or
       config["emojis"] or config["emojis_count"] or
       config["hashtags"] or config["hashtags_count"] or 
       config["mentions"] or config["mentions_count"] ):
        
        try:
            caption=objects["edge_media_to_caption"]["edges"][0]["node"]["text"]
        except:
            caption=""
        
        # Emojis
        def extract_emojis(str):
          return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)
        
        if(config["emojis"] or config["emojis_count"]):
            emojis=extract_emojis(caption) 
        number_of_emojis=len(emojis) if config["emojis_count"] else None
                                      
        # Hashtags            
        def get_rank(n,bounds):
            for i in range(1,len(bounds)):
                if(n<bounds[i]):
                    return i-1
            return i
        
        hashtags=[]
        if(config["hashtags"] or config["hashtags_count"]):
            lst=extract_hash_tags(caption)
            if(len(lst)>0):
                lst=[x.lower() for x in lst]
                hashtags=list(set(lst))
        number_of_hashtags=len(hashtags) if config["hashtags_count"] else None
        
        if(config["hashtags"]):
            for hashtag in hashtags:
                post_link="https://www.instagram.com/explore/tags/"+hashtag+"/"
                r=requests.get(post_link)
                if(r.status_code==200):
                    soup=BeautifulSoup(r.content,'lxml')     			
                    hashtag_objects = json.loads(str(soup).split('<script type="text/javascript">window._sharedData = ')[1].split(';</script>')[0])["entry_data"]["TagPage"][0]["graphql"]['hashtag']
                    hashtag_posts=hashtag_objects["edge_hashtag_to_media"]["count"]
                    hashtag_rank_list[get_rank(hashtag_posts,bounds)].append(hashtag)
            
        # Mentions
        mentions=[]
        if(config["mentions"] or config["mentions_count"]):
            lst=re.findall(r'@([a-zA-Z0-9._]+)',caption)
            if(len(lst)>0):
                lst=[x.lower() for x in lst]
                mentions=list(set(lst))
        number_of_mentions=len(mentions) if config["mentions_count"] else None
        
        temp_caption=caption
        # Remove hashtags
        hashtags=sorted(hashtags, key=len, reverse=True)
        for hashtag in hashtags:
            temp_caption=temp_caption.replace("#"+hashtag,"")
        # Remove emojis
        for emoji1 in emojis:
            temp_caption=temp_caption.replace(emoji1,"")
        # Remove mention
        mentions=sorted(mentions, key=len, reverse=True)
        for mention in mentions:
            temp_caption=temp_caption.replace("@"+mention,"")
            
        for c in string.punctuation:
            temp_caption=temp_caption.replace(c,"")
        
        number_of_chars=len(temp_caption) if config["numb_of_char"] else None
        number_of_words=len(temp_caption.split()) if config["numb_of_words"] else None
        mentions = None if not config["mentions"] else ",".join(mentions)
        emojis = None if not config["emojis"] else emojis
        hashtags = None if not config["hashtags"] else ",".join(hashtags)
        caption = None if not config["full_caption"] else caption
        
    # Mention
    tagged_people=[]
    if(config["tag_accounts"] or config["tag_accounts_count"]):
        for user in objects["edge_media_to_tagged_user"]["edges"]:
            tagged_people.append(user["node"]["user"]["username"])
            
    number_of_tagged_people=len(tagged_people) if config["tag_accounts_count"] else None
    tagged_people=None if not config["tag_accounts"] else ",".join(tagged_people)

#        self.config={'likes_count':bool(self.var_likes_count.get()),
#                 'comments_count':bool(self.var_comments_count.get()),
#                 'engagement_rate':bool(self.var_engagement_rate.get()) if (bool(self.var_likes_count.get()) and bool(self.var_comments_count.get())) else False,
#                 'datetime':bool(self.datetime.get()),
#                 'location':bool(self.var_location.get()),
#                 'tag_accounts_count':bool(self.var_tag_accounts_count.get()),
#                 'tag_accounts':bool(self.var_tag_accounts.get()),
#                 "emojis_count":bool(self.var_emojis_count.get()),
#                 "emojis":bool(self.var_emojis.get()),
#                 "hashtags_count":bool(self.var_hashtags_count.get()),
#                 "hashtags":bool(self.var_hashtags.get()),
#                 "numb_of_words":bool(self.var_numb_of_words.get()),
#                 "numb_of_char":bool(self.var_numb_of_char.get()),
#                 "full_caption":bool(self.var_full_caption.get())
#        }  

    # Comments count
    comments=None
    if(config["comments_count"]):
        comments = objects["edge_media_to_comment"]["count"]
            
        
    # Exact time
    week   = ['Monday', 
              'Tuesday', 
              'Wednesday', 
              'Thursday',  
              'Friday', 
              'Saturday',
              'Sunday']
    date_string=None
    time_string=None
    day_string=None
    month_string=None
    time1 = objects["taken_at_timestamp"]  
    if(config["datetime"]):          
        datetime_string=datetime.utcfromtimestamp(time1).strftime('%m/%d/%Y|%H:%M:%S')
        date_string=datetime_string[0:10]
        time_string=datetime_string[11:21]
    if(config["weekday"]):  
        day_string=week[datetime.utcfromtimestamp(time1).weekday()]
    if(config["month"]):  
        month_string=datetime.utcfromtimestamp(time1).strftime("%B")
        
    # Likes 
    likes=None
    if(config["likes_count"]):
        likes=objects["edge_media_preview_like"]["count"]
    
    # Post type
    post_type=None    
    video_duration=None    
    views=None
    number_of_content=None
    if(objects["__typename"]=="GraphImage"):
        if(config["post_type"]):
            post_type="image"
    elif(objects["__typename"]=="GraphVideo"):
        if(config["post_type"]):
            post_type="video"
        if(config["video_duration"]):
            video_duration=objects["video_duration"]
        if(config["video_views"]):
            views=objects["video_view_count"]
    elif(objects["__typename"]=="GraphSidecar"):
        if(config["post_type"]):
            post_type="gallery"
        if(config["content_count"]):
            number_of_content=len(objects["edge_sidecar_to_children"]["edges"])
            
    headers={   
        "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8'
    }
    
    # Media size, dim, id, links and download
    media_id=objects["id"]
    nb_ressources=len(objects["display_resources"])
    if(objects["__typename"]=="GraphVideo"):
        folder_out=folder_video_location
        download_url=[objects["video_url"]]
        media_dim=[str(objects["display_resources"][nb_ressources-1]['config_width']) \
        + "x"+str(objects["display_resources"][nb_ressources-1]['config_height'])]
    elif(objects["__typename"]=="GraphImage"):
        folder_out=folder_image_location
        download_url=[objects["display_resources"][nb_ressources-1]['src']]
        media_dim=[str(objects["display_resources"][nb_ressources-1]['config_width']) \
        + "x"+str(objects["display_resources"][nb_ressources-1]['config_height'])]
    else:
        download_url=[]
        media_dim=[]
        folder_out=folder_gallery_location+"gallery_"+str(media_id)+"/"        
        for obj in objects["edge_sidecar_to_children"]["edges"]:
            download_url.append(obj['node']["display_resources"][nb_ressources-1]['src'])
            media_dim.append(str(obj['node']["display_resources"][nb_ressources-1]['config_width']) \
            + "x"+str(obj['node']["display_resources"][nb_ressources-1]['config_height']))
        
        create_folder(folder_out)
    
    media_size=[]
    media_location=[]
    media_filename=[]
    import os
    for idx,file_uri in enumerate(download_url):
        media_filename.append(os.path.basename(file_uri))
        path=(folder_out+(os.path.basename(file_uri))).split("?")[0]
        media_location.append(path)
        r=requests.get(file_uri,headers=headers)
        ans_header=r.headers
        media_size.append(str(int(ans_header.get('content-length'))/1000))
        if(r.status_code==200):
            with open(path, 'wb') as f:
                f.write(r.content)    
    
    media_size=",".join(media_size)
    download_url=",".join(download_url)
    media_dim=",".join(media_dim)
    media_location=",".join(media_location)
    media_filename=",".join(media_filename)
    
    # Location
    location_link=None
    location_name=None
    location_id=None
    is_top_nine=None
    top_nine_rank=None
    if(config["location"] and 'location' in objects):
        if(not objects["location"] == None):
            location_link="https://www.instagram.com/explore/locations/%s/%s/" % (objects["location"]["id"],objects["location"]["slug"])
            location_name = objects["location"]["name"]
            location_id = objects["location"]["id"]      
            r=requests.get(location_link)
            if(r.status_code==200):
                soup=BeautifulSoup(r.content,'lxml')  
                location_objects = json.loads(str(soup).split('<script type="text/javascript">window._sharedData = ')[1].split(';</script>')[0])["entry_data"]["LocationsPage"][0]["graphql"]['location']
                top_9=[post["node"]["id"] for post in location_objects["edge_location_to_top_posts"]["edges"]]
                is_top_nine = True if objects["id"] in top_9 else False
                top_nine_rank = top_9.index(objects["id"])+1 if is_top_nine else None
    
    return {
            "is_top_nine":is_top_nine,
            "top_nine_rank":top_nine_rank,
            "location_name":location_name,
            "location_id":location_id,
            "media_size":media_size,
            "download_url":download_url,
            "media_dim":media_dim,
            "media_location":media_location,
            "media_folder_location":folder_out,
            "media_id":media_id,
            "media_filename":media_filename,           
            "post_url":post_url,
            "full_caption":caption,
            "number_of_chars":number_of_chars,
            "number_of_words":number_of_words,
            "hashtag_rank_list":hashtag_rank_list,
            "hashtags":hashtags,
            "number_of_hashtags":number_of_hashtags,
            "emojis":emojis,
            "number_of_emojis":number_of_emojis,
            "tagged_accounts":tagged_people,
            "number_of_tagged_accounts":number_of_tagged_people,
            "location_url":location_link,
            "date":date_string,
            "time":time_string,
            "post_type":post_type,
            "likes":likes,
            "comments":comments,
             "mentions":mentions,
             "mentions_count":number_of_mentions,
             "weekday":day_string,
             "month":month_string,
             "video_duration":video_duration,
             "content_count":number_of_content,
             "video_views":views
            }

def get_post_list(username,N,driver):

    r=requests.get('https://www.instagram.com/'+username)
    number_of_followers=None
    if(r.status_code==200):
        soup=BeautifulSoup(r.content,'lxml')
			
        objects = json.loads(str(soup).split('<script type="text/javascript">window._sharedData = ')[1].split(';</script>')[0])['entry_data']['ProfilePage'][0]['graphql']['user']
	# Get followers count
        number_of_followers=objects['edge_followed_by']['count']
        number_of_post=objects['edge_owner_to_timeline_media']['count']
        if(N==0):
            N=number_of_post
        elif(number_of_post<N):
            N=number_of_post

    driver.get('https://www.instagram.com/'+username)
	
    elems=driver.find_elements_by_class_name("error-container.-cx-PRIVATE-ErrorPage__errorContainer.-cx-PRIVATE-ErrorPage__errorContainer__")
    if(len(elems)>0):
        return {"number_of_followers":0,"list":[]}
    
    end=False
    post_count=0
    
    list_a=[]
    elems=driver.find_elements_by_class_name("Nnq7C.weEfm")
    while(not end):
       
        if(len(list_a)!=0):
            flag=True
            idx=0
            cpt=0
            while(flag):
                link=elems[cpt].find_elements_by_class_name("v1Nh3.kIKUG._bz0w")[0].find_element_by_tag_name("a").get_attribute("href")
                try:
                    idx=list_a.index(link)
                    cpt+=1
                except ValueError:
                    idx=cpt
                    flag=False
        else:
            idx=0
        elems=driver.find_elements_by_class_name("Nnq7C.weEfm")
        elems=elems[idx:len(elems)]
        for elem in elems:
            posts=elem.find_elements_by_class_name("v1Nh3.kIKUG._bz0w")
            for post in posts:
                driver.execute_script("window.scrollTo(0, %s);" % (post.location["y"]-100))
                list_a.append(post.find_element_by_tag_name("a").get_attribute("href"))
                time.sleep(0.1)
                post_count+=1
                print('@{} Getting list of post : {}/{} \r'.format(username,post_count,N))
                if(post_count==N):
                    end=True
                    break
				
                    
            if(end):
                break
    
                    
        elems=driver.find_elements_by_class_name("Nnq7C.weEfm")
    return {"number_of_followers":number_of_followers,"list":list_a}

def writesheet(sheetname,info):
    
    import xlsxwriter
    
    
    workbook = xlsxwriter.Workbook(sheetname,{'strings_to_urls': False})
    worksheet = workbook.add_worksheet()
    worksheet.set_column(0,100,width=50)
    worksheet.set_default_row(40)
    bolds=[]
    
    for i in range(0,24):
        bold = workbook.add_format({'bold': True})
        bold.set_border(2)
        bold.set_align('center')
        bold.set_align('vcenter')
        bolds.append(bold)
        
    time=workbook.add_format({'num_format': 'hh:mm:ss'})
    time.set_align('vcenter')
    time.set_align('center')
    date=workbook.add_format({'num_format': 'mm/dd/yy'})
    date.set_align('vcenter')
    date.set_align('center')
    percent_fmt = workbook.add_format({'num_format': '0.00%'})
    percent_fmt.set_align('vcenter')
    percent_fmt.set_align('center')
    str_fmt=workbook.add_format()
    str_fmt.set_align('vcenter')
    str_fmt.set_align('center')
    
    bolds[0].set_bg_color("#bfbfbf")
    worksheet.write('A1', 'URL of the post',bolds[0])
    
    bolds[1].set_bg_color("#7a7979")
    worksheet.write('B1', 'Full caption',bolds[1])
    
    bolds[2].set_bg_color("#6e708e")
    worksheet.write('C1', 'Number of characters in the caption \n(eliminating hashtags and emojis)',bolds[2])
    
    bolds[3].set_bg_color("#7588e8")
    worksheet.write('D1',
                    'Number of words in the caption \n(eliminating hashtags and emojis)',bolds[3])
    
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('E1',
                    'List of hashtags used in the caption',bolds[4])
    
    bolds[5].set_bg_color("#e0bc5d")
    worksheet.write('F1',
                    'Number of hashtags used in the caption',bolds[5])
    
    bolds[6].set_bg_color("#273666")
    worksheet.write('G1',
                    'List of emojis used in the caption',bolds[6])
    
    bolds[7].set_bg_color("#769636")
    worksheet.write('H1',
                    'Number of emojis',bolds[7])
    
    bolds[8].set_bg_color("#a91414")
    worksheet.write('I1',
                    'Number of likes of the post',bolds[8])
    
    bolds[9].set_bg_color("#ff1a1a")
    worksheet.write('J1',
                    'Number of views of the post (only for video posts)',bolds[9])
    
    bolds[10].set_bg_color("#e0a021")
    worksheet.write('K1',
                    'Number of comments of the post',bolds[10])
    
    bolds[11].set_bg_color("#f3ef07")
    worksheet.write('L1',
                    'Engagement rate of the post',bolds[11])
    
    bolds[12].set_bg_color("#8dcc54")
    worksheet.write('M1',
                    'List of tagged accounts on the post',bolds[12])
    
    bolds[13].set_bg_color("#3f9543")
    worksheet.write('N1',
                    'Number of tagged accounts',bolds[13])
    
    bolds[14].set_bg_color("#6a95f")
    worksheet.write('O1',
                    'List of mentioned accounts in the caption',bolds[14])
    
    bolds[15].set_bg_color("#12537d")
    worksheet.write('P1',
                    'Number of mentioned accounts',bolds[15])
    
    bolds[16].set_bg_color("#ff1eef")
    worksheet.write('Q1',
                    'Location URL',bolds[16])
    
    bolds[17].set_bg_color("#e5812a")
    worksheet.write('R1',
                    'Date when it was posted (year/month/day)',bolds[17])
    
    bolds[18].set_bg_color("#d61f74")
    worksheet.write('S1',
                    'Time when it was posted (24-hour format) (hr:min:sec)',bolds[18])
    
    bolds[19].set_bg_color("#89d61f")
    worksheet.write('T1',
                    'Day of the week',bolds[19])
    
    bolds[20].set_bg_color("#a6f914")
    worksheet.write('U1',
                    'Month of the year',bolds[20])
    
    bolds[21].set_bg_color("#22b5b5")
    worksheet.write('V1',
                    'Post type (Photo, Gallery or Video)',bolds[21])
    
    bolds[22].set_bg_color("#574df8")
    worksheet.write('W1',
                    'Amount of posts (only for gallery posts)',bolds[22])
    
    bolds[23].set_bg_color("#e6ad1f")
    worksheet.write('X1',
                    'Duration of video (only for video posts)',bolds[23])
    
    # Media related columns
    bolds[21].set_bg_color("#22b5b5")
    worksheet.write('B1',
                    'Media ID',bolds[21])
    
    bolds[22].set_bg_color("#574df8")
    worksheet.write('C1',
                    'Downloadable Link',bolds[22])
    
    bolds[23].set_bg_color("#e6ad1f")
    worksheet.write('D1',
                    'Folder Location on PC of Downloaded Media',bolds[23])
    
    bolds[21].set_bg_color("#22b5b5")
    worksheet.write('E1',
                    'Media Location PC',bolds[21])
    
    bolds[22].set_bg_color("#574df8")
    worksheet.write('F1',
                    'Name of The File',bolds[22])
    
    bolds[23].set_bg_color("#e6ad1f")
    worksheet.write('G1',
                    'Media Resolution (in Pixel)',bolds[23])
    
    bolds[23].set_bg_color("#e6ad1f")
    worksheet.write('H1',
                    'Size of the Media (in kB)',bolds[23])
    
    # Location related columns
    bolds[16].set_bg_color("#ff1eef")
    worksheet.write('BU1',
                    'Location URL',bolds[16])
    
    bolds[16].set_bg_color("#ff1eef")
    worksheet.write('BV1',
                    'Location Name',bolds[16])
    
    bolds[16].set_bg_color("#ff1eef")
    worksheet.write('BW1',
                    'Location ID',bolds[16])
    
    bolds[16].set_bg_color("#ff1eef")
    worksheet.write('BX1',
                    'Is the post got featured on TOP 9 posts?',bolds[16])
    
    bolds[16].set_bg_color("#ff1eef")
    worksheet.write('BY1',
                    'In what position it got featured?',bolds[16])
    
    # Hashtag related columns
    
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('S1',
                    'List of hashtags used in the caption',bolds[4])
    
    bolds[5].set_bg_color("#e0bc5d")
    worksheet.write('T1',
                    'Number of hashtags used in the caption',bolds[5])
    
    bolds[5].set_bg_color("#e0bc5d")
    worksheet.write('U1',
                    'List of only unique (most media-related) hashtags used in the caption',bolds[5])
    
    bolds[5].set_bg_color("#e0bc5d")
    worksheet.write('V1',
                    'Number of unique (most media-related) hashtags used in the post',bolds[5])
    
    bolds[5].set_bg_color("#e0bc5d")
    worksheet.write('W1',
                    'Hashtag Uniqueness Coefficient ',bolds[5])
    
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('X1',
                    '0-10k hashtags',bolds[4])
    
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('AA1',
                    '10k-20k hashtags',bolds[4])
    
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('AD1',
                    '20k-50k hashtags',bolds[4])
    
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('AG1',
                    '50k-100k hashtags',bolds[4])
    
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('AJ1',
                    '100k-200k hashtags',bolds[4])
    
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('AM1',
                    '200k-500k hashtags',bolds[4])
    
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('AP1',
                    '500k-2m hashtags',bolds[4])
    
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('AS1',
                    '2m-5m hashtags',bolds[4])
    
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('AV1',
                    '5m and more hashtags',bolds[4])
    
    
    for x in range(0,9):
        
        bolds[5].set_bg_color("#e0bc5d")
        worksheet.write(0,24+3*x,
                        '#',bolds[5])
        
        bolds[5].set_bg_color("#e0bc5d")
        worksheet.write(0,25+3*x,
                        '%',bolds[5])
        
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('AY1',
                    'Amount of the same hashtags used in the caption from previous post caption',bolds[4])

    # Dictionnary related columns
    bolds[4].set_bg_color("#bc7760")
    worksheet.write('AZ1','Number of new words being used in the post caption in comparison from previous caption (eliminating emojis,tags,hashtags, and words are not case sensitive)',bolds[4])

    bolds[4].set_bg_color("#bc7760")
    worksheet.write('BA1','Percentage of the same words being used on second post (elimination of emojis, tags and hashtags being used and words are not case sensitive) (Caption dictonary uniqueness)',bolds[4])

    bolds[4].set_bg_color("#bc7760")
    worksheet.write('BB1','Uniqueness of the caption based on overall data (based on all posts captions)',bolds[4])
    
    

    # END HEADERS
    # Write data
    j=1
    for row in info:
        worksheet.write(j,0,row["post_url"],str_fmt)
        worksheet.write(j,1,row["full_caption"])
        worksheet.write(j,2,row["number_of_chars"],str_fmt)
        worksheet.write(j,3,row["number_of_words"],str_fmt)
        worksheet.write(j,4,row["hashtags"],str_fmt)
        worksheet.write(j,5,row["number_of_hashtags"],str_fmt)
        worksheet.write(j,6,row["emojis"],str_fmt)
        worksheet.write(j,7,row["number_of_emojis"],str_fmt)
        worksheet.write(j,10,row["comments"],str_fmt)
        worksheet.write(j,8,row["likes"],str_fmt)
        try:
            worksheet.write(j,11,row["engagement_rate"],percent_fmt)
        except:
            worksheet.write(j,11,"",str_fmt)
            pass
        worksheet.write(j,12,row["tagged_accounts"],str_fmt)
        worksheet.write(j,13,row["number_of_tagged_accounts"],str_fmt)
        worksheet.write(j,16,row["location_url"],str_fmt)
        
        try:
            date_object = datetime.strptime(row["date"], "%m/%d/%Y")
            worksheet.write(j,17,date_object,date)
        except Exception as e:
            print(e)
            worksheet.write(j,17,"",str_fmt)
            pass
        
        try:
            time_object = datetime.strptime(row["time"], "%H:%M:%S")
            worksheet.write(j,18,time_object,time)
        except:
            worksheet.write(j,18,"",str_fmt)
            pass
        
        worksheet.write(j,19,row['weekday'],str_fmt)
        worksheet.write(j,20,row['month'],str_fmt)
        worksheet.write(j,21,row["post_type"],str_fmt)
        worksheet.write(j,14,row["mentions"],str_fmt)
        worksheet.write(j,15,row["mentions_count"],str_fmt)
        worksheet.write(j,23,row["video_duration"],str_fmt)
        worksheet.write(j,9,row["video_views"],str_fmt)
        worksheet.write(j,22,row["content_count"],str_fmt)
        
        # Media related columns
        worksheet.write(j,1,row["media_id"],str_fmt)
        worksheet.write(j,2,row["download_url"],str_fmt)
        worksheet.write(j,3,row["media_folder_location"],str_fmt)
        worksheet.write(j,4,row["media_location"],str_fmt)
        worksheet.write(j,5,row["media_filename"],str_fmt)
        worksheet.write(j,6,row["media_dim"],str_fmt)
        worksheet.write(j,7,row["media_size"],str_fmt)
        
        # Location related columns
        worksheet.write(j,72,row["location_url"],str_fmt)
        worksheet.write(j,73,row["location_name"],str_fmt)
        worksheet.write(j,74,row["location_id"],str_fmt)
        is_top_nine_str = None if row["is_top_nine"] == None else 'YES' if row["is_top_nine"] else 'NO'
        worksheet.write(j,75,is_top_nine_str,str_fmt)
        worksheet.write(j,76,row["top_nine_rank"],str_fmt)
        
        # Hashtag related columns
        worksheet.write(j,18,row["hashtags"],str_fmt)
        worksheet.write(j,19,row["number_of_hashtags"],str_fmt)
        worksheet.write(j,20, ",".join(row["hashtags_unique"]),str_fmt)
        worksheet.write(j,21,row["hashtags_unique_count"],str_fmt)
        worksheet.write(j,22,row["hashtag_uniqueness"],percent_fmt)
        
        flatten=[item for sublist in row["hashtag_rank_list"] for item in sublist]
        for x in range(0,len(row["hashtag_rank_list"])):
            worksheet.write(j,23+3*x,
                            ",".join(row["hashtag_rank_list"][x]),str_fmt)
            worksheet.write(j,24+3*x,
                            len(row["hashtag_rank_list"][x]),str_fmt)      
            if(len(flatten)>0):
                worksheet.write(j,25+3*x,len(row["hashtag_rank_list"][x])/len(flatten),percent_fmt)
            else:
                worksheet.write(j,25+3*x,0,percent_fmt)
    
        worksheet.write(j,50,row["reused_hashtag_count"],str_fmt)
        
        # Dictionnary related columns
        worksheet.write(j,51,row["new_words_count"],str_fmt)
        worksheet.write(j,52,row["reused_word_percent"],percent_fmt)
        worksheet.write(j,53,row["dictionnary_uniqueness"],percent_fmt)
            
        j+=1
         
    workbook.close()

def scrap(accounts,N,config,output_folder):
    print(N)
    options = Options()
    options.add_argument("--headless")
    #driver = webdriver.Firefox()
    driver = webdriver.Firefox(firefox_options=options,executable_path='../assets/geckodriver')
    output_folder=output_folder.replace("\n","")
    data=[]
    for account in accounts:
        data=[]
        try:
            global folder_image_location, folder_video_location, folder_gallery_location
            create_folder("./outputs/")
            create_folder("./outputs/"+account)
            folder_image_location="./outputs/"+account+"/images/"
            folder_video_location="./outputs/"+account+"/videos/"
            folder_gallery_location="./outputs/"+account+"/galleries/"
            create_folder(folder_image_location)
            create_folder(folder_video_location)
            create_folder(folder_gallery_location)
            res=get_post_list(account,N,driver)  
            cnt=0
            for link in res["list"]:    
                print('@{} Scrapping post : {}/{} \r'.format(account,cnt+1,len(res["list"])))
                scrap=scrap_post(link,config,driver)
                scrap["engagement_rate"]= (scrap["likes"] + scrap["comments"]) / res["number_of_followers"] if config["engagement_rate"] else None
                data.append(scrap)
                time.sleep(1)
                cnt+=1
            # Add overall data
            data=add_overall_analysis(data,config)
                
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
            pass
        
        writesheet(output_folder+"/"+account+".xlsx",data)
        print('@{} Done'.format(account))
    driver.close()
#        with open(output_folder+"/"+account+".csv","w",encoding="utf-8",newline='') as f:
#            spamwriter = csv.writer(f, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL)
#            spamwriter.writerow(['Post URL',
#                                 'Full Caption',
#                                 '# Of Chars',
#                                 '# Of Words',
#                                 'Hashtags',
#                                 'Number Of Hashtags',
#                                 'Emojis',
#                                 '# Of Emojis',
#                                 '# Of Comments',
#                                 '# Of Likes',
#                                 'Engagement Rate',
#                                 'Tagged Accounts',
#                                 '# Of Tagged Accounts',
#                                 'Location URL',
#                                 'Date',
#                                 'Time',
#                                 'Day',
#                                 'Month',
#                                 'Post Type',
#                                 'Mentions',
#                                 '# Of Mentions',
#                                 'Video Duration',
#                                 'Video Views',
#                                 '# Of Content'
#                                 ])
#            for row in data:
#                spamwriter.writerow([row["post_url"],
#                row["full_caption"],
#                row["number_of_chars"],
#                row["number_of_words"],
#                row["hashtags"],
#                row["number_of_hashtags"],
#                row["emojis"],
#                row["number_of_emojis"],
#                row["comments"],
#                row["likes"],
#                row["engagement_rate"],
#                row["tagged_accounts"],
#                row["number_of_tagged_accounts"],
#                row["location_url"],
#                row["date"],
#                row["time"],
#                row['weekday'],
#                row['month'],
#                row["post_type"],
#                row["mentions"],
#                row["mentions_count"],
#                row["video_duration"],
#                row["video_views"],
#                row["content_count"]
#                ])
            

        
    
    
    
    
#scrap_post("https://www.instagram.com/p/BmbVg2djQsI/?taken-by=natoogram")




        

