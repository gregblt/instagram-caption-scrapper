#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 16:16:34 2018

@author: gregory
"""
import time
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
import re
import emoji
import sys, traceback
import csv
from selenium.webdriver.firefox.options import Options




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
        hashtags=[]
        if(config["hashtags"] or config["hashtags_count"]):
            lst=re.findall(r'#([^\s]+)',caption)
            if(len(lst)>0):
                lst=[x.lower() for x in lst]
                hashtags=list(set(lst))
        number_of_hashtags=len(hashtags) if config["hashtags_count"] else None
        
        # Mentions
        mentions=[]
        if(config["mentions"] or config["mentions_count"]):
            lst=re.findall(r'@([a-zA-Z0-9._]+)',caption)
            if(len(lst)>0):
                lst=[x.lower() for x in lst]
                mentions=list(set(lst))
        number_of_mentions=len(mentions) if config["mentions_count"] else None
        
        temp_caption=caption
        # Remove emojis
        for emoji1 in emojis:
            temp_caption=temp_caption.replace(emoji1,"")
        # Remove hashtags
        for hashtag in hashtags:
            temp_caption=temp_caption.replace("#"+hashtag,"")
        # Remove mention
        for mention in mentions:
            temp_caption=temp_caption.replace("@"+mention,"")
        
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
        datetime_string=datetime.utcfromtimestamp(time1).strftime('%m.%d.%Y|%H:%M:%S')
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
    

    location_link=None
    if(config["location"] and 'location' in objects):
        if(not objects["location"] == None):
            location_link="https://www.instagram.com/explore/locations/%s/%s/" % (objects["location"]["id"],objects["location"]["slug"])
        
    
    return {"post_url":post_url,
            "full_caption":caption,
            "number_of_chars":number_of_chars,
            "number_of_words":number_of_words,
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
                if(post_count==N):
                    end=True
                    break
                else:
                    print('%s/%s' % (post_count,N))
            if(end):
                break
    
                    
        elems=driver.find_elements_by_class_name("Nnq7C.weEfm")
    return {"number_of_followers":number_of_followers,"list":list_a}

def scrap(accounts,N,config,output_folder):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox()
    #driver = webdriver.Firefox(firefox_options=options)
    output_folder=output_folder.replace("\n","")
    data=[]
    for account in accounts:
        data=[]
        try:
            res=get_post_list(account,N,driver)  
            cnt=0
            for link in res["list"]:
                scrap=scrap_post(link,config,driver)
                scrap["engagement_rate"]= (scrap["likes"] + scrap["comments"]) / res["number_of_followers"] if config["engagement_rate"] else None
                scrap["full_caption"]=scrap["full_caption"].replace("\n","") if config["full_caption"] else None
                data.append(scrap)
                time.sleep(1)
                cnt+=1
                print('%s/%s' % (cnt,N))
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
            pass
                
        with open(output_folder+"/"+account+".csv","w",encoding="utf-8",newline='') as f:
            spamwriter = csv.writer(f, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL)
            spamwriter.writerow(['Post URL',
                                 'Full Caption',
                                 '# Of Chars',
                                 '# Of Words',
                                 'Hashtags',
                                 'Number Of Hashtags',
                                 'Emojis',
                                 '# Of Emojis',
                                 '# Of Comments',
                                 '# Of Likes',
                                 'Engagement Rate',
                                 'Tagged Accounts',
                                 '# Of Tagged Accounts',
                                 'Location URL',
                                 'Date',
                                 'Time',
                                 'Day',
                                 'Month',
                                 'Post Type',
                                 'Mentions',
                                 '# Of Mentions',
                                 'Video Duration',
                                 'Video Views',
                                 '# Of Content'
                                 ])
            for row in data:
                spamwriter.writerow([row["post_url"],
                row["full_caption"],
                row["number_of_chars"],
                row["number_of_words"],
                row["hashtags"],
                row["number_of_hashtags"],
                row["emojis"],
                row["number_of_emojis"],
                row["comments"],
                row["likes"],
                row["engagement_rate"],
                row["tagged_accounts"],
                row["number_of_tagged_accounts"],
                row["location_url"],
                row["date"],
                row["time"],
                row['weekday'],
                row['month'],
                row["post_type"],
                row["mentions"],
                row["mentions_count"],
                row["video_duration"],
                row["video_views"],
                row["content_count"]
                ])
            
    driver.close()
        
    
    
    
    
#scrap_post("https://www.instagram.com/p/BmbVg2djQsI/?taken-by=natoogram")




        

