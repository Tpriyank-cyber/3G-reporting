import streamlit as st
import pandas as pd
import os

def calculate_kpis(df):
    required_columns = ['CS_RRC_Num_M', 'CS_RRC_Denum_M', 'PS_RRC_Num_M', 'PS_RRC_Denum_M', 'CS_RAB_Num_M', 'CS_RAB_Denum_M', 'PS_RAB_Num_M', 'PS_RAB_Denum_M', 'CSDROPNOM_C', 'CSDROPDENOM_C', 'HSDROP_NUM_V', 'HSDROP_DENOM_V']
    
    df.columns = df.columns.str.strip()  # Remove any leading/trailing spaces in column names
    
    st.write("Available Columns:", df.columns.tolist())  # Debugging: Print column names
    
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return df  # Return original DataFrame to prevent crashes
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)  # Convert to numeric
    
    df['CS RRC SR'] = (df['CS_RRC_Num_M'] / df['CS_RRC_Denum_M']) * 100
    df['PS RRC SR'] = (df['PS_RRC_Num_M'] / df['PS_RRC_Denum_M']) * 100
    df['CS RAB SR'] = (df['CS_RAB_Num_M'] / df['CS_RAB_Denum_M']) * 100
    df['PS RAB SR'] = (df['PS_RAB_Num_M'] / df['PS_RAB_Denum_M']) * 100
    df['CS DCR'] = (df['CSDROPNOM_C'] / df['CSDROPDENOM_C']) * 100
    df['HS DCR'] = (df['HSDROP_NUM_V'] / df['HSDROP_DENOM_V']) * 100
    return df

st.title("KPI Data Processing")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df['Period start time'] = pd.to_datetime(df['Period start time'], errors='coerce')
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
