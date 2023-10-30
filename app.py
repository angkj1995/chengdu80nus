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
from datetime import datetime

st.set_page_config(layout="wide")
debug = 'data/'

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
    news = pd.read_csv(debug+string+'_news_yahoo_sent.csv')
    # news = pd.read_csv('data/'+string+'_news_yahoo.csv')
    news = news.drop(news.columns[0], axis=1).loc[:,['date','sentiment','title','desc','source','url']]

    #Output news
    with st.expander("Recent company news"):
      #Function to colour columns
      def colorful_sentiment(value):
        return f"background-color: pink;" if value in ["negative"] else f"background-color: lightgreen;" if value in ["positive"] else None
      st.dataframe(news.style.applymap(colorful_sentiment), 
                   #Column link to URL
                   column_config={"url": st.column_config.LinkColumn()},
                   use_container_width =True)
 

    cola, colb = st.columns(2)
    with cola:
      #Download news
      st.download_button("Press to Download",
      news.to_csv(),
      "file.csv",
      "text/csv",
      key='download-csv')
    with colb:
      #Want to compare to s&p?
      compare = st.checkbox(label='Compare to S&P500')

    col1, col2 = st.columns(2)
    with col1:
      # # importing the yfinance package
      import yfinance as yf

      # giving the start and end dates
      startDate = '2022-10-29'
      endDate = datetime.now().strftime(format='%Y-%m-%d')

      # downloading the data of the ticker value between
      # the start and end dates
      resultData = yf.download(string, startDate, endDate)
      # resultData = pd.read_csv(debug+string+'_price.csv')
      # resultData = resultData.set_index('Date')

      if compare:

        # importing the yfinance package
        import yfinance as yf

        # giving the start and end dates
        startDate = '2022-10-29'
        endDate = datetime.now().strftime(format='%Y-%m-%d')

        # downloading the data of the ticker value between
        # the start and end dates
        resultData2 = yf.download('%5EGSPC', startDate, endDate)
        # resultData2 = pd.read_csv(debug+'S&P500_price.csv')
        # resultData2 = resultData2.set_index('Date')

        rebase = pd.concat([resultData.rename(columns={'Close':string}),resultData2.rename(columns={'Close':'S&P500'})], axis=1)
        rebase = (rebase / rebase.iloc[0]) * 100 -100
        fig = px.line(rebase, x=rebase.index, y=[string, 'S&P500'], title=ticker+ ' against S&P500', labels={'value': 'Cumulative Return (%)'})
        st.write(fig)
      else:

        fig = px.line(resultData, x=resultData.index, y='Close', title=ticker+ ' Over Time',
                      labels={'Close': 'Stock Price (USD)'})
        st.write(fig)
    
    with col2:
      #Define function that maps sentiments to numerics
      def mapsent(x):
          return 1 if x=='positive' else -1 if x=='negative' else 0 

      news['sentiment_val'] = news['sentiment'].apply(mapsent)
      senti_line = news.groupby('date')['sentiment_val'].agg(lambda x: x.sum()/x.count())

      fig2 = px.line(senti_line, x=senti_line.index, y=['sentiment_val'], title='News Sentiment of '+string, 
      labels={'date': 'Date', 'value': 'Sentiment'})

      fig2.add_shape(type='line', x0=senti_line.index.min(), x1=senti_line.index.max(),
          y0=0, y1=0, line=dict(color='black', width=1, dash='dash') )

      st.write(fig2)

