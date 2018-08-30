#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 12:44:36 2018

@author: gregory
"""

import scrapper
import json
import re
import emoji
import string

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

list_post=["https://www.instagram.com/p/Bm1sVjcAGbf/",
"https://www.instagram.com/p/Bm1ZJc0gINY/",
"https://www.instagram.com/p/BmyZwdnA5dO/",
"https://www.instagram.com/p/BmwJnHUAGOi/",
"https://www.instagram.com/p/BmtriTAArCA/"]

list_data=[]
config={'likes_count':True,
                 'comments_count':True,
                 'engagement_rate':True,
                 'datetime':True,
                 'location':True,
                 'tag_accounts_count':True,
                 'tag_accounts':True,
                 "emojis_count":True,
                 "emojis":True,
                 "hashtags_count":True,
                 "hashtags":True,
                 "numb_of_words":True,
                 "numb_of_char":True,
                 "full_caption":True,
                 "post_link":True,
                 "post_type":True,
                 "mentions":True,
                 "mentions_count":True,
                 "weekday":True,
                 "month":True,
                 "video_duration":True,
                 "content_count":True,
                 "video_views":True
        }  
        
for post_link in list_post:
    list_data.append(scrapper.scrap_post(post_link,config,None)) 
    
    
with open("dat_overall.json","r") as f:
    list_data=json.loads(f.read())


# Hashtags reused
old_hashtags=list_data[len(list_data)-1]["hashtags"].split(",")
reused_hashtag_count_list=[]
reused_hashtag_count_list.append(None)
for data in reversed(list_data[:-1]):
    current_hashtags=data["hashtags"].split(",")
    reused_hashtag_count_list.insert(0,
                                     len([value for value in current_hashtags if value in old_hashtags]))
    old_hashtags=current_hashtags


# Word reused or not
words_overall=[]

full_cap=list_data[len(list_data)-1]["full_caption"]

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

data2 = scrapper.add_overall_analysis(list_data,config)
        
