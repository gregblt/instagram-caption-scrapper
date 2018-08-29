#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 23:02:29 2018

@author: gregory
"""



PROXY_HOST = "64.137.191.20:3128"


from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType

prox = Proxy()
prox.proxy_type = ProxyType.MANUAL
prox.http_proxy = PROXY_HOST
prox.socks_proxy = PROXY_HOST
prox.ssl_proxy = PROXY_HOST

capabilities = webdriver.DesiredCapabilities.CHROME
prox.add_to_capabilities(capabilities)

driver = webdriver.Chrome(desired_capabilities=capabilities)