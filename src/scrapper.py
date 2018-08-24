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

def scrap_post(post_link,config,driver):    


#    
    driver.get(post_link)
    
    # URL
    post_url = post_link
    

    if(config["full_caption"] or config["numb_of_char"] or config["numb_of_words"] or config["emojis"] or 
       config["emojis_count"] or config["tag_accounts"] or config["tag_accounts_count"] or
       config["hashtags"] or config["hashtags_count"]):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "C4VMK"))
            )
            caption=element.find_element_by_tag_name("span").text 
        except:
            caption=""
        
        number_of_chars=len(caption) if config["numb_of_char"] else None
        number_of_words=len(caption.split()) if config["numb_of_words"] else None
        # Emojis
        def extract_emojis(str):
          return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)
        
        if(config["emojis"] or config["emojis_count"]):
            emojis=extract_emojis(caption) 
            number_of_emojis=len(emojis) if config["emojis_count"] else None
            emojis = None if not config["emojis"] else emojis
            
        # Mention
        if(config["tag_accounts"] or config["tag_accounts_count"]):
            lst=re.findall(r'@([a-zA-Z0-9._]+)',caption)
            tagged_people=[]
            if(len(lst)>0):
                lst=[x.lower() for x in lst]
                tagged_people=list(set(lst))
            number_of_tagged_people=len(tagged_people) if config["tag_accounts_count"] else None
            tagged_people=None if not config["tag_accounts"] else tagged_people
                               
        # Hashtags
        if(config["hashtags"] or config["hashtags_count"]):
            lst=re.findall(r'#([^\s]+)',caption)
            hashtags=[]
            if(len(lst)>0):
                lst=[x.lower() for x in lst]
                hashtags=list(set(lst))
            number_of_hashtags=len(hashtags) if config["hashtags_count"] else None
            hashtags = None if not config["hashtags"] else hashtags
            
        caption = None if not config["full_caption"] else caption

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
        r=requests.get(post_link)
        if(r.status_code==200):
            soup=BeautifulSoup(r.content,'lxml')     			
            objects = json.loads(str(soup).split('<script type="text/javascript">window._sharedData = ')[1].split(';</script>')[0])
            comments = objects["entry_data"]["PostPage"][0]["graphql"]['shortcode_media']["edge_media_to_comment"]["count"]
            
        
    # Exact time
    time_string=None
    if(config["datetime"]):
        time1 = driver.find_element_by_tag_name('time').get_attribute('datetime')
        time1=time1[0:19]
        
        datetime_object = datetime.strptime(time1, '%Y-%m-%dT%H:%M:%S')
        time_string=datetime_object.strftime('%m_%d_%Y at %H:%M:%S')
    

    
    # Post type
    post_type=None
    likes=None
    

    article=driver.find_elements_by_tag_name("article")
    
    article_soup=BeautifulSoup(article[0].get_attribute("innerHTML"),'lxml')
    likes=None
    
    if(len(str(article_soup).split("kPFhm B1JlO"))>1):
        try:
            driver.execute_script("window.scrollTo(0, %s);" % (driver.find_element_by_class_name("vcOH2").location["y"]-100))
            driver.find_element_by_class_name("vcOH2").click()
            if(config["likes_count"]):
                likes=int(driver.find_element_by_class_name("vJRqr").find_element_by_tag_name("span").text.replace(',',''))       
            post_type='video'
        except NoSuchElementException:
            if(config["likes_count"]):
                likes=int(driver.find_element_by_class_name("zV_Nj").find_element_by_tag_name("span").text.replace(',',''))
            post_type='gallery'
            pass
    elif(len(str(article_soup).split("eLAPa kPFhm"))>1 or len(str(article_soup).split("eLAPa _23QFA"))>1):
        if(config["likes_count"]):
            likes=int(driver.find_element_by_class_name("zV_Nj").find_element_by_tag_name("span").text.replace(',',''))
        post_type='photo'
    elif(len(str(article_soup).split("rQDP3"))>1):
        if(config["likes_count"]):
            likes=int(driver.find_element_by_class_name("zV_Nj").find_element_by_tag_name("span").text.replace(',',''))
        post_type='gallery'
        

    
    # Location
    loc=None
    location_link=None
    if(config["location"]):
        locs=driver.find_elements_by_class_name("O4GlU")
        location_link=None
        for loc in locs:
            location_link=loc.get_attribute('href')
        
    
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
            "datetime":time_string,
            "post_type":post_type,
            "likes":likes,
            "comments":comments
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
            if(end):
                break
    
                    
        elems=driver.find_elements_by_class_name("Nnq7C.weEfm")
    return {"number_of_followers":number_of_followers,"list":list_a}

def scrap(accounts,N,config,output_folder):
    driver = webdriver.Firefox()
    output_folder=output_folder.replace("\n","")
    data=[]
    for account in accounts:
        try:
            res=get_post_list(account,N,driver)    
            for link in res["list"]:
                scrap=scrap_post(link,config,driver)
                scrap["engagement_rate"]= (scrap["likes"] + scrap["comments"]) / res["number_of_followers"] if config["engagement_rate"] else None
                data.append(scrap)
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
            pass
                
        with open(output_folder+"/"+account+".csv","w") as f:
            spamwriter = csv.writer(f, delimiter=',')
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
                                 'Datetime',
                                 'Post Type'])
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
                row["datetime"],
                row["post_type"],
                ])
            
    driver.close()
        
    
    
    
    
#scrap_post("https://www.instagram.com/p/BmbVg2djQsI/?taken-by=natoogram")




        

