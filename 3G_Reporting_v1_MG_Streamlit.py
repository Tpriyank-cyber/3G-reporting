import streamlit as st
import pandas as pd

# Streamlit App Title
st.title("📊 3G KPI Data Processing Tool")

# Upload file
uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

# Dropdown for sheet selection
sheet_type = st.selectbox("Select sheet type:", ["BBH", "Continue"])

# Define KPI Columns
KPI_Obj = [
    'CS RRC SR', 'PS RRC SR', 'CS RAB SR', 'PS RAB SR', 'CS DCR', 'HS DCR',
    'Act HS-DSCH end usr thp', 'CellAvailabilityexcluding', 'CS Traffic',
    'Inter sys RT Hard HO SR', 'Max simult HSDPA users', 'PS Traffic',
    'SHO_SR_M', 'Average RTWP'
]

# Function to calculate KPIs
def calculate_kpis(df):
    df['CS RRC SR'] = df.apply(lambda x: (x['CS_RRC_Num_M'] / x['CS_RRC_Denum_M']) * 100 if x['CS_RRC_Denum_M'] != 0 else 0, axis=1)
    df['PS RRC SR'] = df.apply(lambda x: (x['PS_RRC_Num_M'] / x['PS_RRC_Denum_M']) * 100 if x['PS_RRC_Denum_M'] != 0 else 0, axis=1)
    df['CS RAB SR'] = df.apply(lambda x: (x['CS_RAB_Num_M'] / x['CS_RAB_Denum_M']) * 100 if x['CS_RAB_Denum_M'] != 0 else 0, axis=1)
    df['PS RAB SR'] = df.apply(lambda x: (x['PS_RAB_Num_M'] / x['PS_RAB_Denum_M']) * 100 if x['PS_RAB_Denum_M'] != 0 else 0, axis=1)
    df['CS DCR'] = df.apply(lambda x: (x['CSDROPNOM_C'] / x['CSDROPDENOM_C']) * 100 if x['CSDROPDENOM_C'] != 0 else 0, axis=1)
    df['HS DCR'] = df.apply(lambda x: (x['HSDROP_NUM_V'] / x['HSDROP_DENOM_V']) * 100 if x['HSDROP_DENOM_V'] != 0 else 0, axis=1)
    return df

# Button to Process File
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['Start Time'] = pd.to_datetime(df['Period start time'], errors='coerce')
    df['Date'] = df['Start Time'].dt.date
    df['Hour'] = df['Start Time'].dt.hour
    df = calculate_kpis(df)
    
    # Selecting Processing Type
    if sheet_type == "BBH":
        pivot = pd.pivot_table(df, index=['RNC name', 'WBTS name'], columns='Date', values=KPI_Obj, aggfunc='sum')
        output_filename = "3G_Day_Site_Level_KPIs_output.xlsx"
    else:
        selected_hour = st.number_input("Select Hour (0-23):", min_value=0, max_value=23, step=1)
        if selected_hour >= 0:
            df = df[df['Hour'] == selected_hour]
        pivot = pd.pivot_table(df, index=['RNC name', 'WCEL name'], columns='Date', values=KPI_Obj, aggfunc='sum')
        output_filename = "3G_Day_Cell_Level_KPIs_output.xlsx"
    
    pivot = pivot.stack(level=0).reset_index(drop=False)
    pivot.rename(columns={'level_1': 'KPI NAME'}, inplace=True)
    
    st.success("✅ Data Processed Successfully!")
    st.dataframe(pivot.head())
    
    # Convert to CSV for Download
    csv = pivot.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Processed Data", csv, output_filename, "text/csv")
