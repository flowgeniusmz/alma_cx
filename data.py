import streamlit as st
import pandas as pd
import numpy as np
from typing import Literal
from simple_salesforce import Salesforce
from datetime import datetime

st.set_page_config(page_title="Alma CX", layout="wide", initial_sidebar_state="collapsed")
# Cache Salesforce data with a TTL of 24 hours (86400 seconds)
@st.cache_data(ttl=86400)
def get_sfdc_data(type: Literal['30day', '90day', '180day']):
    if type == "30day":
        query = st.secrets.salesforce.query_30
    elif type == "90day":
        query = st.secrets.salesforce.query_90
    elif type == "180day":
        query = st.secrets.salesforce.query_180
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

# Function to add aging column to DataFrame
def add_aging_column(df: pd.DataFrame):
    # Ensure the Customer_Warranty_End_Date__c is a datetime object
    df['Customer_Warranty_End_Date__c'] = pd.to_datetime(df['Customer_Warranty_End_Date__c'], errors='coerce')
    
    # Calculate the difference in days between today and the warranty end date
    today = pd.to_datetime(datetime.today().date())  # Get today's date
    df['Aging'] = (df['Customer_Warranty_End_Date__c'] - today).dt.days  # Difference in days (can be negative)
    
    return df

# Streamlit app
st.title("Customer Warranty Data")

# Create tabs for 30, 90, and 180-day views
tabs = st.tabs(["30 Days", "90 Days", "180 Days"])

# Fetch and display data for each tab
with tabs[0]:
    st.subheader("Warranties Ending in the Next 30 Days")
    df_30 = get_sfdc_data(type="30day")
    df_30_with_aging = add_aging_column(df_30)
    st.dataframe(df_30_with_aging, use_container_width=True)

with tabs[1]:
    st.subheader("Warranties Ending in the Next 90 Days")
    df_90 = get_sfdc_data(type="90day")
    df_90_with_aging = add_aging_column(df_90)
    st.dataframe(df_90_with_aging, use_container_width=True)

with tabs[2]:
    st.subheader("Warranties Ending in the Next 180 Days")
    df_180 = get_sfdc_data(type="180day")
    df_180_with_aging = add_aging_column(df_180)
    st.dataframe(df_180_with_aging, use_container_width=True)
