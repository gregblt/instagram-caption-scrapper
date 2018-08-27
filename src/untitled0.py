#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 14:17:05 2018

@author: gregory
"""

import xlsxwriter
    
    
workbook = xlsxwriter.Workbook("lol.xlsx")
worksheet = workbook.add_worksheet()
worksheet.set_column(0,23,width=50)
worksheet.set_default_row(50)
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

from datetime import datetime
time_object = datetime.strptime(None, "%H:%M:%S")
worksheet.write('A1',time_object,time)

workbook.close( )