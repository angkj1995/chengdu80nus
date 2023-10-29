# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 15:21:08 2023

@author: KJ
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup
import time
import plotly.express as px
import yfinance as yf
import datetime

debug = 'C:/users/kj/Desktop/chengdu80-nus/data/'

#Title home page
st.title('Welcome to NUS Finovators Demo! 👋')
st.write('**👈 Select a module from the sidebar**')
st.markdown("""
            1. Global Macroeconomic News
            2. Industry Specific Analysis
            3. Company Specific Analysis
            4. Value Chain Analysis""")

#Summary page on news
st.header('II. Summary Page')
st.subheader('Select the company you want to investigate')
#Selector bar
ticker = st.selectbox(label='', options=['Apple Inc. (AAPL)','Microsoft Corporation (MSFT)','NVIDIA Corporation (NVDA)'], index=None, placeholder='Select Stock...') 

 
if not (ticker is None):
    #String cleaning and read news
    string = ticker[-5:-1]
    news = pd.read_csv('data/'+string+'_news_yahoo.csv')
    news = news.drop(news.columns[0], axis=1).iloc[:,[4,0,1,3,2]]

    #Output news
    with st.expander("Recent company news"):
      st.dataframe(news)

    #Download news
    st.download_button("Press to Download",
    news.to_csv(),
    "file.csv",
    "text/csv",
    key='download-csv')

    col1, col2 = st.columns(2)
    with col1:
      # importing the yfinance package
      import yfinance as yf

      # giving the start and end dates
      startDate = '2022-10-29'
      endDate = today.strftime(format='%Y-%m-%d')

      # downloading the data of the ticker value between
      # the start and end dates
      resultData = yf.download(string, startDate, endDate)
      fig = px.line(resultData, x=resultData.index, y='Close', title=ticker+ ' Over Time')
      st.write(fig)

