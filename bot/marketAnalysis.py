# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 22:31:07 2021

@author: shujain8
"""

import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import io

def getDate(date=''):    
    if(date==''):
        if(datetime.datetime.now().hour>19):
            date = datetime.datetime.now()
        else:
            date = (datetime.datetime.now()-datetime.timedelta(1))
    
    #Excluding Saturday and sunday and taking friday as current date
    if(date.weekday()>4):
        date = (datetime.datetime.now()-datetime.timedelta(1)).strftime('%d%m%Y') if date.weekday==5 else (datetime.datetime.now()-datetime.timedelta(2)).strftime('%d%m%Y')
    else:
        date = date.strftime('%d%m%Y')
    return date
    
  
def getURL(date):
    url = {
    'HEALTHCARE': 'https://www1.nseindia.com/content/indices/ind_niftyhealthcarelist.csv',
    'AUTO': 'https://www1.nseindia.com/content/indices/ind_niftyautolist.csv',
    'BANK': 'https://www1.nseindia.com/content/indices/ind_niftybanklist.csv',
    'CONSUMER': 'https://www1.nseindia.com/content/indices/ind_niftyconsumerdurableslist.csv',
    'FINANACE': 'https://www1.nseindia.com/content/indices/ind_niftyfinancelist.csv',
    'FINANCE25_50': 'https://www1.nseindia.com/content/indices/ind_niftyfinancialservices25_50list.csv',
    'FMCG': 'https://www1.nseindia.com/content/indices/ind_niftyfmcglist.csv',
    'IT': 'https://www1.nseindia.com/content/indices/ind_niftyitlist.csv',
    'MEDIA': 'https://www1.nseindia.com/content/indices/ind_niftymedialist.csv',
    'METAL': 'https://www1.nseindia.com/content/indices/ind_niftymetallist.csv',
    'OILANDGAS': 'https://www1.nseindia.com/content/indices/ind_niftyoilgaslist.csv',
    'PHARMA': 'https://www1.nseindia.com/content/indices/ind_niftypharmalist.csv',
    'PRIVATEBANK': 'https://www1.nseindia.com/content/indices/ind_nifty_privatebanklist.csv',
    'PSUBANK': 'https://www1.nseindia.com/content/indices/ind_niftypsubanklist.csv',
    'REALTY': 'https://www1.nseindia.com/content/indices/ind_niftyrealtylist.csv',
    'SMEEMRGE': 'https://www1.nseindia.com/content/indices/ind_niftysmelist.csv',
    'COMMODITIES': 'https://www1.nseindia.com/content/indices/ind_niftycommoditieslist.csv',
    'CPSE': 'https://www1.nseindia.com/content/indices/ind_niftycpselist.csv',
    'ENERGY': 'https://www1.nseindia.com/content/indices/ind_niftyenergylist.csv',
    'CONSUMPTION': 'https://www1.nseindia.com/content/indices/ind_niftyconsumptionlist.csv',
    'INFRA': 'https://www1.nseindia.com/content/indices/ind_niftyinfralist.csv',
    'MNC': 'https://www1.nseindia.com/content/indices/ind_niftymnclist.csv',
    'PSE': 'https://www1.nseindia.com/content/indices/ind_niftypselist.csv',
    'LIQUID15': 'https://www1.nseindia.com/content/indices/ind_niftyservicelist.csv',
    'BHAVCOPY': f'https://archives.nseindia.com/products/content/sec_bhavdata_full_{date}.csv',
    'INDICES': f'https://archives.nseindia.com/content/indices/ind_close_all_{date}.csv',
    }
    return url


def dailyMarketAnalysis(date=''):
    date = getDate(date)
    url = getURL(date)
    #Best Performing stock
    bhavCopy = pd.read_csv(url['BHAVCOPY'])
    bhavCopy.columns = bhavCopy.columns.str.replace(' ', '')
    bhavCopy['%Change'] = ((bhavCopy['CLOSE_PRICE']-bhavCopy['PREV_CLOSE'])/bhavCopy['PREV_CLOSE'])*100
    bhavCopy.loc[bhavCopy['%Change']>=0, 'Change'] = 'Positive'
    bhavCopy.loc[bhavCopy['%Change']<0, 'Change'] = 'Negative'
    highReturnsSecurities = bhavCopy.sort_values(by='%Change', ascending=False)[:10]
    highVolume = bhavCopy.sort_values(by='TTL_TRD_QNTY', ascending=False)[:10]
    bestPerformingSecurities = bhavCopy.loc[(bhavCopy['%Change']>3)].sort_values(by='TTL_TRD_QNTY', ascending=False)[:10]
    worstPerformingSecurities = bhavCopy.loc[(bhavCopy['%Change']<0)].sort_values(by='TTL_TRD_QNTY', ascending=False)[:10]
    highVolumePalette = ['tomato', 'mediumslateblue'] if highVolume['%Change'].iloc[0]<0 else ['mediumslateblue', 'tomato']
    
    
    stocks = {'Top 10 Securities with highest returns today': highReturnsSecurities, 
              'Top 10 Best performing securities with high volume today': bestPerformingSecurities,
              'Top 10 Worst performing securities with High volume today': worstPerformingSecurities,
             'Top 10 Securities with highest traded volume': highVolume}
    
    stockPalette = {'Top 10 Securities with highest returns today': ["mediumslateblue"], 
              'Top 10 Best performing securities with high volume today': ['mediumslateblue'],
              'Top 10 Worst performing securities with High volume today': ['tomato'],
             'Top 10 Securities with highest traded volume': highVolumePalette}

    figs = {'d1': io.BytesIO(),
            'd2': io.BytesIO(),
            'd3': io.BytesIO(),
            'd4': io.BytesIO()}
    
    k = 0
    for n,i in stocks.items():
        k += 1
        g = sns.catplot(y='SYMBOL', x='%Change', data=i, hue='Change', kind = 'bar',palette=stockPalette[n], dodge=False)
        g.fig.set_size_inches(15, 5)
        g.fig.suptitle(n)
        g.fig.subplots_adjust(top=0.81, right=0.86)
        ax = g.facet_axis(0, 0)
        for c in ax.containers:
            labels = [f'{(v.get_width()):.1f}%' for v in c]
            ax.bar_label(c, labels=labels, label_type='edge')
        g.savefig(figs[f'd{k}'])
        
    return figs
