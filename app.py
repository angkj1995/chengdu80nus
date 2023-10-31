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
import json

st.set_page_config(layout="wide")
debug = 'data/'

# Title and introductory text for the home page
st.title('Welcome to NUS Finovators Demo! 👋')
st.write('**👈 Select a module from the sidebar**')
st.markdown("""
            1. Global Macroeconomic News
            2. Industry Specific Analysis
            3. Company Specific Analysis
            4. Value Chain Analysis""")

# Header and subheader for the "Company Specific Analysis" section
st.header('3. Company Specific Analysis')
st.subheader('Select the company you want to investigate')
# Dropdown selector for choosing a company
ticker = st.selectbox(label='', options=['Apple Inc. (AAPL)','Microsoft Corporation (MSFT)','NVIDIA Corporation (NVDA)'], index=None, placeholder='Select Stock...') 

 
if not (ticker is None):
    # Extract the stock ticker from the selected company
    string = ticker[-5:-1]
    # Read news data from a CSV file
    news = pd.read_csv(debug+string+'_news_yahoo_sent.csv')
    # news = pd.read_csv('data/'+string+'_news_yahoo.csv')
    news = news.drop(news.columns[0], axis=1).loc[:,['date','sentiment','title','desc','source','url']]


    # Display the recent company news in an expander
    with st.expander("Recent company news"):
      # Function to color code sentiment in the dataframe
      def colorful_sentiment(value):
        return f"background-color: pink;" if value in ["negative"] else f"background-color: lightgreen;" if value in ["positive"] else None
      st.dataframe(news.style.applymap(colorful_sentiment), 
                   #Column link to URL
                   column_config={"url": st.column_config.LinkColumn()},
                   use_container_width =True)
 
    #Company summary
    st.write("**Summary of Recent company news**")
    coy_summary = json.load(open(debug+string+'_summary.json'))
    st.text(coy_summary['text'])

    # Create two columns for UI layout
    cola, colb = st.columns(2)
    with cola:
      # Download button to export the news data to a CSV file
      st.download_button("Download all recent company news",
      news.to_csv(),
      "file.csv",
      "text/csv",
      key='download-csv')
    with colb:
      # Checkbox to choose whether to compare with S&P500
      compare = st.checkbox(label='Compare to S&P500')


    # Create two columns for plotting data
    col1, col2 = st.columns(2)
    with col1:
      # importing the yfinance package
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

        # Normalize and compare stock and S&P500 data
        rebase = pd.concat([resultData.rename(columns={'Close':string}),resultData2.rename(columns={'Close':'S&P500'})], axis=1)
        rebase = (rebase / rebase.iloc[0]) * 100 -100
        # Create a plot for the comparison
        fig = px.line(rebase, x=rebase.index, y=[string, 'S&P500'], title=ticker+ ' against S&P500', 
                      labels={'value': 'Cumulative Return (%)'})
        st.plotly_chart(fig, use_container_width=True)
      
      else:
        # Create a plot for the stock price over time
        fig = px.line(resultData, x=resultData.index, y='Close', title=ticker+ ' Over Time',
                      labels={'Close': 'Stock Price (USD)'})
        st.plotly_chart(fig, use_container_width=True)
    

    with col2:
      # Define a function that maps sentiments to numerical values
      def mapsent(x):
          return 1 if x=='positive' else -1 if x=='negative' else 0 

      # Add a numerical sentiment column to the news dataframe
      news['sentiment_val'] = news['sentiment'].apply(mapsent)

      # Calculate and plot the sentiment trend over time
      senti_line = news.groupby('date')['sentiment_val'].agg(lambda x: x.sum()/x.count())
      fig2 = px.line(senti_line, x=senti_line.index, y='sentiment_val', title='News Sentiment of '+string, 
      labels={'date': 'Date', 'sentiment_val': 'Sentiment'})

      # Change the line color and add a horizontal dashed line at y=0
      fig2.update_traces(line_color='orange')
      fig2.add_shape(type='line', x0=senti_line.index.min(), x1=senti_line.index.max(),
          y0=0, y1=0, line=dict(color='black', width=1, dash='dash') )

      st.plotly_chart(fig2,use_container_width=True)


    st.subheader("News Impact Analysis")
    # Create two columns for plotting data
    col3, col4 = st.columns(2)

    with col3:
      st.markdown("What is the impact of recent **:red[Negative News]** on "+ticker+"?")
      # st.write('What is the impact of **Negative News** on '+ticker+"?")
      neg_impact = pd.read_json((debug+string+'_negative_impact.json'))
      neg_news = st.selectbox(label='', options=neg_impact['negative_news'], index=None, placeholder='Select Negative News...')
      if neg_news is not None:
        st.write(neg_impact[neg_impact['negative_news']==neg_news].iloc[0,1])

    with col4:
      st.markdown("What is the impact of recent **:green[Positive News]** on "+ticker+"?")
      # st.write('What is the impact of **Negative News** on '+ticker+"?")
      pos_impact = pd.read_json((debug+string+'_positive_impact.json'))
      pos_news = st.selectbox(label='', options=pos_impact['positive_news'], index=None, placeholder='Select Positive News...')
      if pos_news is not None:
        st.write(pos_impact[pos_impact['positive_news']==pos_news].iloc[0,1])      



    st.subheader("**Value Chain Analysis**")
    st.write("""Firms frequently mentioned alongside """+ticker+""" in news articles are extracted and plotted 
    to show the tight-knit relationship with """+ticker+""". Large nodes indicate a higher co-occurance in news articles""")

    #Read graph data
    graph = pd.read_csv(debug+string+'_links_fix.csv')
    graph = graph.drop(graph.columns[0], axis=1).groupby('Key').sum('Value').reset_index()
    if string=='MSFT':
      graph = graph[graph['Value']>=3]
    else:
      graph = graph[graph['Value']>=5]
    graph['source'] = string
    graph['target'] = graph['Key']
    graph['weight'] = graph['Value']

    #Create the graph and node weights
    Graphtype = nx.Graph()
    G = nx.from_pandas_edgelist(graph, edge_attr='weight',create_using=Graphtype)
    weighted_degrees = dict(G.degree(weight='weight'))

    # Step 3: Plot the graph with node sizes proportional to their weighted degrees
    node_sizes = [15 * weighted_degrees[node] for node in G.nodes()]
    node_sizes[0] = min(node_sizes)

    net = plt.figure()
    nx.draw_networkx(G, node_size=node_sizes)
    st.pyplot(net) 
