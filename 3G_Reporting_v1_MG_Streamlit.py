import streamlit as st
import pandas as pd
import os

def calculate_kpis(df):
    df['CS RRC SR'] = df.apply(lambda x: (x['CS_RRC_Num_M'] / x['CS_RRC_Denum_M']) * 100 if x['CS_RRC_Denum_M'] != 0 else 0, axis=1)
    df['PS RRC SR'] = df.apply(lambda x: (x['PS_RRC_Num_M'] / x['PS_RRC_Denum_M']) * 100 if x['PS_RRC_Denum_M'] != 0 else 0, axis=1)
    df['CS RAB SR'] = df.apply(lambda x: (x['CS_RAB_Num_M'] / x['CS_RAB_Denum_M']) * 100 if x['CS_RAB_Denum_M'] != 0 else 0, axis=1)
    df['PS RAB SR'] = df.apply(lambda x: (x['PS_RAB_Num_M'] / x['PS_RAB_Denum_M']) * 100 if x['PS_RAB_Denum_M'] != 0 else 0, axis=1)
    df['CS DCR'] = df.apply(lambda x: (x['CSDROPNOM_C'] / x['CSDROPDENOM_C']) * 100 if x['CSDROPDENOM_C'] != 0 else 0, axis=1)
    df['HS DCR'] = df.apply(lambda x: (x['HSDROP_NUM_V'] / x['HSDROP_DENOM_V']) * 100 if x['HSDROP_DENOM_V'] != 0 else 0, axis=1)
    return df

st.title("KPI Data Processing")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df['Period start time'] = pd.to_datetime(df['Period start time'])
    df['Date'] = df['Period start time'].dt.date
    
    level = st.radio("Select Processing Level", ["Day Level", "Hourly Level", "BBH Level"])
    
    if level == "Day Level":
        df = calculate_kpis(df)
        st.write("Day Level Processing Complete")
    elif level == "Hourly Level":
        df['Hour'] = df['Period start time'].dt.hour
        df = calculate_kpis(df)
        st.write("Hourly Level Processing Complete")
    elif level == "BBH Level":
        df = calculate_kpis(df)
        st.write("BBH Level Processing Complete")
    
    st.write("Processed Data:")
    st.dataframe(df.head())
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Processed Data", csv, "processed_data.csv", "text/csv")
