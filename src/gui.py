#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 10:55:35 2018

@author: gregory
"""

from tkinter import filedialog
import tkinter as tk
from tkinter import ttk  
import os
import scrapper

from threading import Thread

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

# définition du thread
class MonThread (Thread) :
    def __init__ (self, win, res, accounts,N,config,output_folder) :
        Thread.__init__ (self)
        self.win = win  # on mémorise une référence sur la fenêtre
        self.res = res
        self.accounts=accounts
        self.N=N
        self.config=config
        self.output_folder=output_folder

    def run (self) :
        r=scrapper.scrap(self.accounts,self.N,self.config,self.output_folder)
        self.res.append(r)

          # on lance un événement <<thread_fini>> à la fenêtre principale
          # pour lui dire que le thread est fini, l'événement est ensuite
          # géré par la boucle principale de messages
          # on peut transmettre également le résultat lors de l'envoi du message
          # en utilisant un attribut de la classe Event pour son propre compte
        self.win.event_generate("<<thread_fini>>")

thread_resultat = []

class App():
    
    checkboxes=[]
    
    def thread_fini_fonction (self,e) :
        global thread_resultat
          # fonction appelée lorsque le thread est fini
        # self.checkboxes
        for button in self.checkboxes:
            button.config(state="normal")
        # Browse
        self.b_browse.config(state="normal")
        
        # Run
        self.b_run.config(state="normal")
        
        self.l_running.config (text = "Done")
        
        # User inputs
        self.in_N.config(state="normal")
        self.entry.config(state="normal")
        self.entry_button.config(state="normal")


    def browse_button(self):
            # Allow user to select a directory and store it in global var
            # called folder_path
            global folder_path
            filename = filedialog.askdirectory()
            n=30
            filename=[filename[i:i+n] for i in range(0, len(filename), n)]
            filename_str=""
            if(len(filename)>1):
                for line in filename:
                    filename_str+=line
                    filename_str+='\n'
            else:
                filename_str+=filename[0]
            self.folder_path.set(filename_str)
            print(filename)
    
    
                
    def on_run(self):
        # Disable everything
        
        # self.checkboxes
        for button in self.checkboxes:
            button.config(state="disabled")
        # Browse
        self.b_browse.config(state="disabled")
        
        # Run
        self.b_run.config(state="disabled")
        
        self.l_running=tk.Label(master=self.log,text="Running...")
        self.l_running.grid(row=5, column=0)
        
        # User inputs
        self.in_N.config(state="disabled")
        self.entry.config(state="disabled")
        self.entry_button.config(state="disabled")
        
#        # Progress bar
#        self.l_general_progress = tk.Label(master=root,text="Total progress")
#        self.l_general_progress.grid(row=5, column=0)
#        self.downloaded=0
#        self.progress= ttk.Progressbar(self.root, length=400, orient = 'horizontal', maximum = 100, value = self.downloaded)
#        self.progress.grid(row=6,column=0)
#        
#        # sub Progress bar
#        self.l_local_progress = tk.Label(master=root,text="Getting @natoogram posts")
#        self.l_local_progress.grid(row=7, column=0)
#        self.local_downloaded=0
#        self.local_progress= ttk.Progressbar(self.root, length=400, orient = 'horizontal', maximum = 100, value = self.local_downloaded)
#        self.local_progress.grid(row=8,column=0)
    
        
#        ## Step 1 : Getting posts
#        def cb(arg):
#            print(arg)
#            
#        self.thread = Thread(target = untitled8.get_post_list,args=("natoogram",10),callback=cb)
#        self.thread.deamon=True
#        self.thread.start()

        global thread_resultat
          # fonction appelée lors de la pression du bouton
          # on change la légnde de la zone de texte
          
        self.config={'likes_count':bool(self.var_likes_count.get()),
                 'comments_count':bool(self.var_comments_count.get()),
                 'engagement_rate':bool(self.var_engagement_rate.get()) if (bool(self.var_likes_count.get()) and bool(self.var_comments_count.get())) else False,
                 'datetime':bool(self.var_datetime.get()),
                 'location':bool(self.var_location.get()),
                 'tag_accounts_count':bool(self.var_tag_accounts_count.get()),
                 'tag_accounts':bool(self.var_tag_accounts.get()),
                 "emojis_count":bool(self.var_emojis_count.get()),
                 "emojis":bool(self.var_emojis.get()),
                 "hashtags_count":bool(self.var_hashtags_count.get()),
                 "hashtags":bool(self.var_hashtags.get()),
                 "numb_of_words":bool(self.var_numb_of_words.get()),
                 "numb_of_char":bool(self.var_numb_of_char.get()),
                 "full_caption":bool(self.var_full_caption.get())
        }  

        m = MonThread (self.root, 
                       thread_resultat,
                       self.user_list,
                       int(self.var_N.get()),
                       self.config,
                       self.folder_path.get())
        m.start ()


        
    def on_likes_count_change(self):
        
            if(self.var_likes_count.get()==0):
                self.b_engagement_rate.config(state="disabled")
            else:
                if(self.var_comments_count.get()==1):
                    self.b_engagement_rate.config(state="normal")
            
    def on_comments_count_change(self):
    
        if(self.var_comments_count.get()==0):
            self.b_engagement_rate.config(state="disabled")
        else:
            if(self.var_likes_count.get()==1):
                self.b_engagement_rate.config(state="normal")
        
    def __init__(self, master):
        
        self.root = master
        self.folder_select = tk.Frame(root)
        self.folder_select.grid(row=0)
        self.user_area = tk.Frame(root, borderwidth=2)
        self.user_area.grid(row=1)
        self.checkbox_area = tk.Frame(root, borderwidth=2, relief="solid")
        self.checkbox_area.grid(row=2)
        self.log = tk.Frame(root, borderwidth=2)
        self.log.grid(row=3)
        
        
        self.folder_path = tk.StringVar()
        n=30
        filename=os.getcwd()
        filename=[filename[i:i+n] for i in range(0, len(filename), n)]
        filename_str=""
        if(len(filename)>1):
            for line in filename:
                filename_str+=line
                filename_str+='\n'
        else:
            filename_str+=filename[0]
        self.folder_path.set(filename_str)
        self.lbl1 = tk.Label(master=self.folder_select,textvariable=self.folder_path)
        self.lbl1.grid(row=0, column=1)
        self.lbl2 = tk.Label(master=self.folder_select,text="Output directory :")
        self.lbl2.grid(row=0, column=0)
        self.b_browse = tk.Button(master=self.folder_select,text="Browse", command=self.browse_button)
        self.b_browse.grid(row=0, column=2)
        
        def check(a,b,c):
            #if(var_N.get()[len(var_N.get())])
            if(len(self.var_N.get())>0):
                if(not self.var_N.get()[len(self.var_N.get())-1].isdigit()):
                    self.var_N.set(self.var_N.get()[0:(len(self.var_N.get())-1)])

                
        
        self.var_N=tk.StringVar()
        self.var_N.trace('w',check)
        self.l_N = tk.Label(master=self.user_area,text="Number of post")
        self.l_N.grid(row=0, column=0)
        self.in_N = tk.Spinbox(master=self.user_area, from_=0,
                               to=999999999999999999,
                               textvariable=self.var_N)
        self.in_N.grid(row=0, column=1)
        # usernames
        self.user_list=[]
        
        def addUser():
            self.user_list.append(self.entry_val.get())
            tk.Label(master=self.user_area,text=self.user_list[len(self.user_list)-1]).grid(row=len(self.user_list)+1, column=0)

        
        self.entry_label = tk.Label(master=self.user_area,text="User to scrap :")
        self.entry_label.grid(row=1, column=0)
        
        self.entry_val=tk.StringVar()
        self.entry=tk.Entry(master=self.user_area,textvariable=self.entry_val)
        self.entry.grid(row=1,column=1)
        
        self.entry_button=tk.Button(master=self.user_area,text="Add",command=addUser)
        self.entry_button.grid(row=1,column=2)
        
        # Define checkboxes 
        self.var_full_caption=tk.IntVar()
        self.var_full_caption.set(1)
        self.var_numb_of_char=tk.IntVar()
        self.var_numb_of_char.set(1)
        self.var_numb_of_words=tk.IntVar()
        self.var_numb_of_words.set(1)
        self.var_hashtags=tk.IntVar()
        self.var_hashtags.set(1)
        self.var_hashtags_count=tk.IntVar()
        self.var_hashtags_count.set(1)
        self.var_emojis=tk.IntVar()
        self.var_emojis.set(1)
        self.var_emojis_count=tk.IntVar()
        self.var_emojis_count.set(1)
        self.var_comments_count=tk.IntVar()
        self.var_comments_count.set(1)
        self.var_likes_count=tk.IntVar()
        self.var_likes_count.set(1)
        self.var_engagement_rate=tk.IntVar()
        self.var_engagement_rate.set(1)
        self.var_tag_accounts=tk.IntVar()
        self.var_tag_accounts.set(1)
        self.var_tag_accounts_count=tk.IntVar()
        self.var_tag_accounts_count.set(1)
        self.var_location=tk.IntVar()
        self.var_location.set(1)
        self.var_datetime=tk.IntVar()
        self.var_datetime.set(1)
        
        etiqs=['Full caption',
        '# of characters',
        '# of words',
        'Hashtags',
        '# of hashtags',
        'Emojis',
        'Number of emojis',
        '# of comments',
        '# of likes',
        'Engagement rate',
        'Tagged accounts',
        '# of tagged accounts',
        'Location URL',
        'Date & Time']
        
        self.b_full_caption = tk.Checkbutton(self.checkbox_area, variable=self.var_full_caption, text=etiqs[0])
        self.b_full_caption.grid(row=1, column=0)
        self.checkboxes.append(self.b_full_caption)
        
        self.b_numb_of_char = tk.Checkbutton(self.checkbox_area, variable=self.var_numb_of_char, text=etiqs[1])
        self.b_numb_of_char.grid(row=1, column=1)
        self.checkboxes.append(self.b_numb_of_char)
        
        self.b_numb_of_words = tk.Checkbutton(self.checkbox_area, variable=self.var_numb_of_words, text=etiqs[2])
        self.b_numb_of_words.grid(row=1, column=2)
        self.checkboxes.append(self.b_numb_of_words)
        
        self.b_hashtags = tk.Checkbutton(self.checkbox_area, variable=self.var_hashtags, text=etiqs[3])
        self.b_hashtags.grid(row=1, column=3)
        self.checkboxes.append(self.b_hashtags)
        
        self.b_hashtags_count = tk.Checkbutton(self.checkbox_area, variable=self.var_hashtags_count, text=etiqs[4])
        self.b_hashtags_count.grid(row=1, column=4)
        self.checkboxes.append(self.b_hashtags_count)
        
        self.b_emojis = tk.Checkbutton(self.checkbox_area, variable=self.var_emojis, text=etiqs[5])
        self.b_emojis.grid(row=1, column=5)
        self.checkboxes.append(self.b_emojis)
        
        self.b_emojis_count = tk.Checkbutton(self.checkbox_area, variable=self.var_emojis_count, text=etiqs[6])
        self.b_emojis_count.grid(row=2, column=0)
        self.checkboxes.append(self.b_emojis_count)
        
        self.b_engagement_rate = tk.Checkbutton(self.checkbox_area, variable=self.var_engagement_rate, text=etiqs[9])
        self.b_engagement_rate.grid(row=2, column=3)
        self.checkboxes.append(self.b_engagement_rate)
        
        self.b_likes_count = tk.Checkbutton(self.checkbox_area, variable=self.var_likes_count, text=etiqs[8], command=self.on_likes_count_change)
        self.b_likes_count.grid(row=2, column=2)
        self.checkboxes.append(self.b_likes_count)
        
        self.b_comments_count = tk.Checkbutton(self.checkbox_area, variable=self.var_comments_count, text=etiqs[7], command=self.on_comments_count_change)
        self.b_comments_count.grid(row=2, column=1)
        self.checkboxes.append(self.b_comments_count)
        
        self.b_tag_accounts = tk.Checkbutton(self.checkbox_area, variable=self.var_tag_accounts, text=etiqs[10])
        self.b_tag_accounts.grid(row=2, column=4)
        self.checkboxes.append(self.b_tag_accounts)
        
        self.b_tag_accounts_count = tk.Checkbutton(self.checkbox_area, variable=self.var_tag_accounts_count, text=etiqs[11])
        self.b_tag_accounts_count.grid(row=2, column=5)
        self.checkboxes.append(self.b_tag_accounts_count)
        
        self.b_location = tk.Checkbutton(self.checkbox_area, variable=self.var_location, text=etiqs[12])
        self.b_location.grid(row=3, column=0)
        self.checkboxes.append(self.b_location)
        
        self.b_datetime = tk.Checkbutton(self.checkbox_area, variable=self.var_datetime, text=etiqs[13])
        self.b_datetime.grid(row=3, column=1)
        self.checkboxes.append(self.b_datetime)
        
        self.b_run = tk.Button(self.log,text="Run", command=self.on_run)
        self.b_run.grid(row=4, column=2)
        

if __name__ == "__main__":
    root = tk.Tk()
    gui = App(root)
    # on associe une fonction à un événement <<thread_fini>> propre au programme
    root.bind ("<<thread_fini>>", gui.thread_fini_fonction)
    root.mainloop()
    