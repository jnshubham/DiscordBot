import io
from df2img import df2img
import gspread
import pandas as pd
import datetime
import math
from oauth2client.service_account import ServiceAccountCredentials

def connect():
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    return client


def displayData(itype, status, time):
    client = connect()
    if(itype=.lower()='swing'):
        sheet = client.open("Summary").worksheet('Swing')  # Open the spreadhseet
        df = pd.DataFrame(sheet.get_all_records())
        if(status.lower() in ('open','closed')):
            filterMask = df['Status']==status.capitalize()
            df = df.loc[filterMask]
        if(time!=''):
            month = datetime.datetime.strptime(time,'%b').month
            year = datetime.datetime.now().year
            filterMask = ((pd.to_datetime(df['CallDate'], format='%Y-%m-%d').dt.month==month) & (pd.to_datetime(df['CallDate'], format='%Y-%m-%d').dt.year==year))
            df = df.loc[filterMask]
    elif(itype.lower()=='positional'):
        sheet = client.open("Summary").worksheet('Positional')  # Open the spreadhseet
        df = pd.DataFrame(sheet.get_all_records())
        if(status.lower() in ('open','closed')):
            filterMask = df['Status']==status.capitalize()
            df = df.loc[filterMask]
        if(time!=''):
            month = datetime.datetime.strptime(time,'%b').month
            year = datetime.datetime.now().year
            filterMask = ((pd.to_datetime(df['CallDate'], format='%Y-%m-%d').dt.month==month) & (pd.to_datetime(df['CallDate'], format='%Y-%m-%d').dt.year==year))
            df = df.loc[filterMask]
    return df
            

def df2imgs(df):
    data_stream = io.BytesIO()
    df2img(
        df,
        file=data_stream,
        header_color="white",
        header_bgcolor="darkred",
        row_bgcolors=["lightgray", "white"],
    )
    return data_stream

def addInvestmentCall(data):
    client = connect()
    sheet = client.open("Summary").worksheet('Swing')  # Open the spreadhseet
    datad = {}
    for i in data.split('\n')[1:5]:
        datad[i.split(':')[0].lower()] = i.split(':')[1].strip()

    t1,t2,t3, *_ = map(lambda x:x.strip(),datad['targets'].split('/')+['0','0'])
    row = [datad['security'], str(datetime.datetime.today().strftime('%Y-%m-%d')),
             int(datad['cmp']), int(datad['sl']),None,
             datad['targets'],None, None,None,None,None,None,None,None,None,'Open',None]
    df = pd.DataFrame(sheet.get_all_records())
    #df['StockName'] = 'test'
    df.loc[len(df)] = row
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    
    
def updateInvestmentCall(data):
    client = connect()
    sheet = client.open("Summary").worksheet('Swing')  # Open the spreadhseet
    df = pd.DataFrame(sheet.get_all_records())
    datad = {}
    for i in data.split('\n')[1:4]:
        datad[i.split(':')[0].lower()] = i.split(':')[1].strip()
    mask = (df['StockName']==datad['security']) & (df['Status']=='Open')
    dataList = [datad['cmp'], str(datetime.datetime.now().strftime('%Y-%m-%d')),
                    str(datetime.datetime.now()-datetime.datetime.strptime(df.loc[mask,'CallDate'].tolist()[0],'%Y-%m-%d')).split(' ')[0] if 'day' in str(datetime.datetime.now()-datetime.datetime.strptime(df.loc[mask,'CallDate'].tolist()[0],'%Y-%m-%d')) else 1.0,
                    ((float(datad['cmp'])-float(df.loc[mask,'BuyPrice']))/float(df.loc[mask,'BuyPrice']))*100.0,
                    float(((float(datad['cmp'])-float(df.loc[mask,'BuyPrice']))/float(df.loc[mask,'BuyPrice']))*100.0)/(math.ceil(float(str(datetime.datetime.now()-datetime.datetime.strptime(df.loc[mask,'CallDate'].tolist()[0],'%Y-%m-%d')).split(' ')[0] if 'day' in str(datetime.datetime.now()-datetime.datetime.strptime(df.loc[mask,'CallDate'].tolist()[0],'%Y-%m-%d')) else 1.0)/30.0))
                    ]
    if(datad['event'].lower().startswith('t1')):
        dataList.append('Target1 Achieved')
        df.loc[mask,['Target1', 'Target1Date', 'Time', 'TotalROI', 'MonthlyROI', 'Remarks']]=dataList
    elif(datad['event'].lower().startswith('t2')):
        dataList.append('Target2 Achieved')
        df.loc[mask,['Target2', 'Target2Date', 'Time', 'TotalROI', 'MonthlyROI', 'Remarks']]=dataList
    elif(datad['event'].lower().startswith('t3')):
        dataList.append('Target3 Achieved')
        df.loc[mask,['Target3', 'Target3Date', 'Time', 'TotalROI', 'MonthlyROI', 'Remarks']]=dataList
        df.loc[mask, 'Status']='Closed'
    elif(datad['event'].lower().startswith('sl')):
        dataList.append('SL Hit')
        df.loc[mask,['StopLoss', 'SLDate', 'Time', 'TotalROI', 'MonthlyROI', 'Remarks']]=dataList
        df.loc[mask, 'Status']='Closed'
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    
def addPositionalCall(data):
    client = connect()
    sheet = client.open("Summary").worksheet('Positional')  # Open the spreadhseet
    datad = {}
    for i in data.split('\n')[1:3]:
        datad[i.split(':')[0].lower()] = i.split(':')[1].strip()    
    row = [datad['security'], 
             int(datad['cmp']), 
             str(datetime.datetime.today().strftime('%Y-%m-%d')),None,None,None,'Open']
    df = pd.DataFrame(sheet.get_all_records())
    #df['StockName'] = 'test'
    df.loc[len(df)] = row
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    

def updatePositionalCall(data):
    client = connect()
    sheet = client.open("Summary").worksheet('Positional')  # Open the spreadhseet
    df = pd.DataFrame(sheet.get_all_records())
    datad = {}
    for i in data.split('\n')[1:3]:
        datad[i.split(':')[0].lower()] = i.split(':')[1].strip()
    mask = (df['StockName']==datad['security']) & (df['Status']=='Open')
    dataList = [datad['cmp'], str(datetime.datetime.now().strftime('%Y-%m-%d')),
              ((float(datad['cmp'])-float(df.loc[mask,'BuyPrice']))/float(df.loc[mask,'BuyPrice']))*100.0,
               ]
    df.loc[mask,['HighPrice', 'HighDate', 'ROI']]=dataList   
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    
    
    
# client = connect()
# status='open'
# print(status)
# sheet = client.open("Summary").worksheet('Swing')  # Open the spreadhseet
# df = pd.DataFrame(sheet.get_all_records())

# print(df)
# import io
# data_stream = io.BytesIO()
# from df2img import df2img

# df2img(
#     df,
#     file='test.png',
#     header_color="white",
#     header_bgcolor="darkred",
#     row_bgcolors=["lightgray", "white"],
# )