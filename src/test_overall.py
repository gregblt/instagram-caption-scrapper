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
from collections import Counter

def extract_hash_tags(s):
    l = s.split("#")[1:]
    res = []
    for v in l:
        res.append(v.split(" ")[0])
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
    
# emojis
emojis_overall=[item for sublist in [data["emojis"] for data in list_data] for item in sublist]
number_of_emojis_average='%.1f'%(len(emojis_overall)/len(list_data))
emojis_overall=list(set(emojis_overall))
number_of_emojis_overall=len(emojis_overall)

    
day=[data['weekday'] for data in list_data]
most_common,num_most_common = Counter(day).most_common(1)[0]

percent_gallery=None
percent_image=None
percent_video=None
types=[data['post_type'] for data in list_data]
if  types:
    percent_gallery=Counter(types)['gallery']/len(types)
    percent_image=Counter(types)['image']/len(types)
    percent_video=Counter(types)['video']/len(types)


number_of_words_overall= [ data['number_of_words'] for data in list_data ]
if(len([float(i) for i in number_of_words_overall])>0):
    number_of_words_average = '%.1f'%(sum([float(i) for i in number_of_words_overall])/len([float(i) for i in number_of_words_overall]))
else:
    number_of_words_average = 0
    
number_of_hashtags_average = None
if([ data['number_of_hashtags'] for data in list_data ]):
    number_of_hashtags_average = '%.1f'%(sum([ data['number_of_hashtags'] for data in list_data ])/len([ data['number_of_hashtags'] for data in list_data ]))
else:
    number_of_hashtags_average = 0

hashtags_overall=[data["hashtags"].split(",") for data in list_data]

unique_overall=[]
non_unique_overall=[]
for hashtag_list in hashtags_overall:
    unique=[]
    non_unique=[]
    for hashtag in hashtag_list:
        if(sum([hashtag in hashtag_list_t for hashtag_list_t in hashtags_overall])==1):
            unique.append(hashtag)
        else:
            non_unique.append(hashtag)
    unique_overall.append(unique)
    non_unique_overall.append(non_unique)
    
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
word_non_unique_overall=[]
for word_list in words_overall:
    word_unique=[]
    word_non_unique=[]
    for word in word_list:
        if(sum([word_list_t.count(word) for word_list_t in words_overall])==1):
            word_unique.append(word)
        else:
            word_non_unique.append(word)
    word_non_unique_overall.append(word_non_unique)
    word_unique_overall.append(word_unique)
    
word_unique_overall_flat=list(set([item for sublist in word_unique_overall for item in sublist]))
word_non_unique_overall_flat=list(set([item for sublist in word_non_unique_overall for item in sublist]))
    
dictionnary_uniqueness=[]
for i in range(0,len(words_overall)):
    if(len(words_overall[i])==0):
        dictionnary_uniqueness.append(0)
    else:
        dictionnary_uniqueness.append(
                (len(word_unique_overall[i]))/(len(words_overall[i]))
                )

hashtag_rank_list_overall=[[] for i in range(len(data['hashtag_rank_list']))]
for idx in range(0,len(data['hashtag_rank_list'])):
    hashtag_rank_list_overall[idx]=([item for sublist in [data['hashtag_rank_list'][idx] for data in list_data] for item in sublist])


a,b = scrapper.add_overall_analysis(list_data,config)
        
