import streamlit as st
from simple_salesforce import Salesforce
import pandas as pd
import requests
from typing import Literal
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Alma CX", layout="wide", initial_sidebar_state="collapsed")
# Cache Salesforce data with a TTL of 24 hours (86400 seconds)
@st.cache_data(ttl=86400)
def get_sfdc_data(type: Literal['30day', '90day', '180day']):
    if type == "30day":
        query = st.secrets.salesforce.req_30
    elif type == "90day":
        query = st.secrets.salesforce.req_90
    elif type == "180day":
        query = st.secrets.salesforce.req_180
    sfClient = Salesforce(username=st.secrets.salesforce.username, password=st.secrets.salesforce.password, security_token=st.secrets.salesforce.security_token)
    data = sfClient.query(query=query)
    df = pd.DataFrame(data['records']).drop('attributes', axis=1)
    listColumns = list(df.columns)
    for col in listColumns:
        if any(isinstance(df[col].values[i], dict) for i in range(0, len(df[col].values))):
            df = pd.concat([df.drop(columns=[col]), df[col].apply(pd.Series, dtype=df[col].dtype).drop('attributes', axis=1).add_prefix(col + '.')], axis=1)
            new_columns = np.setdiff1d(df.columns, listColumns)
            for i in new_columns:
                listColumns.append(i)
    return df

def send_30_day_emails(df):
    url = st.secrets.requests.url
    for index, row in df.iterrows():
        payload = {"type": "30Day", "warranty_end_date": row['Customer_Warranty_End_Date__c'], "account": row['Account__c'], "email": "cxspecialist@almalasers.com"}
        try:
            response = requests.post(url=url, json=payload)
        except Exception as e:
            print(e)

def send_90_day_emails(df):
    url = st.secrets.requests.url
    for index, row in df.iterrows():
        payload = {"type": "90Day", "warranty_end_date": row['Customer_Warranty_End_Date__c'], "account": row['Account__c'], "email": "cxspecialist@almalasers.com"}
        try:
            response = requests.post(url=url, json=payload)
        except Exception as e:
            print(e)
            

def send_180_day_emails(df):
    url = st.secrets.requests.url
    for index, row in df.iterrows():
        payload = {"type": "180Day", "warranty_end_date": row['Customer_Warranty_End_Date__c'], "account": row['Account__c'], "email": "cxspecialist@almalasers.com"}
        try:
            response = requests.post(url=url, json=payload)
        except Exception as e:
            print(e)
            

df30 = get_sfdc_data(type="30day")
df90 = get_sfdc_data(type="90day")
df180 = get_sfdc_data(type="180day")
send_30_day_emails(df30)
send_90_day_emails(df90)
send_180_day_emails(df180)