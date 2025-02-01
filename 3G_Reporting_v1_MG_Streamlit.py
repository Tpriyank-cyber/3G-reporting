import streamlit as st
import pandas as pd
import os

def calculate_kpis(df):
    required_columns = ['CS_RRC_Num_M', 'CS_RRC_Denum_M', 'PS_RRC_Num_M', 'PS_RRC_Denum_M', 'CS_RAB_Num_M', 'CS_RAB_Denum_M', 'PS_RAB_Num_M', 'PS_RAB_Denum_M', 'CSDROPNOM_C', 'CSDROPDENOM_C', 'HSDROP_NUM_V', 'HSDROP_DENOM_V']
    
    df.columns = df.columns.str.strip()
    
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return df
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['CS RRC SR'] = (df['CS_RRC_Num_M'] / df['CS_RRC_Denum_M']) * 100
    df['PS RRC SR'] = (df['PS_RRC_Num_M'] / df['PS_RRC_Denum_M']) * 100
    df['CS RAB SR'] = (df['CS_RAB_Num_M'] / df['CS_RAB_Denum_M']) * 100
    df['PS RAB SR'] = (df['PS_RAB_Num_M'] / df['PS_RAB_Denum_M']) * 100
    df['CS DCR'] = (df['CSDROPNOM_C'] / df['CSDROPDENOM_C']) * 100
    df['HS DCR'] = (df['HSDROP_NUM_V'] / df['HSDROP_DENOM_V']) * 100
    return df

def process_data(df, level):
    df['Start Time'] = pd.to_datetime(df['Period start time'], errors='coerce')
    df['Date'] = df['Start Time'].dt.date
    df = calculate_kpis(df)
    
    if level == "Day Level":
        pivot = pd.pivot_table(df, index=['PLMN Name'], columns='Date', values=['CS RRC SR', 'PS RRC SR', 'CS RAB SR', 'PS RAB SR'], aggfunc='sum')
    elif level == "Hourly Level":
        df['Hour'] = df['Start Time'].dt.hour
        pivot = pd.pivot_table(df, index=['RNC name', 'WCEL name'], columns=['Date', 'Hour'], values=['CS RRC SR', 'PS RRC SR'], aggfunc='sum')
    elif level == "BBH Level":
        pivot = pd.pivot_table(df, index=['RNC name', 'WBTS name'], columns='Date', values=['CS RRC SR', 'PS RRC SR'], aggfunc='sum')
    else:
        st.error("Invalid processing level selected.")
        return None
    
    return pivot.reset_index()

st.title("3G KPI Data Processing")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    
    level = st.radio("Select Processing Level", ["Day Level", "Hourly Level", "BBH Level"])
    
    if st.button("Process Data"):
        processed_df = process_data(df, level)
        if processed_df is not None:
            st.write("Processed Data:")
            st.dataframe(processed_df.head())
            csv = processed_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Processed Data", csv, "processed_data.csv", "text/csv")
