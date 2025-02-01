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

required_columns = [
    'CS_RRC_Num_M', 'CS_RRC_Denum_M', 'PS_RRC_Num_M', 'PS_RRC_Denum_M',
    'CS_RAB_Num_M', 'CS_RAB_Denum_M', 'PS_RAB_Num_M', 'PS_RAB_Denum_M',
    'CSDROPNOM_C', 'CSDROPDENOM_C', 'HSDROP_NUM_V', 'HSDROP_DENOM_V'
]

# Function to calculate KPIs
def calculate_kpis(df):
    for col in required_columns:
        if col not in df.columns:
            st.warning(f"Missing column: {col}. Filling with 0.")
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['CS RRC SR'] = (df['CS_RRC_Num_M'] / df['CS_RRC_Denum_M']).replace([float('inf'), -float('inf')], 0) * 100
    df['PS RRC SR'] = (df['PS_RRC_Num_M'] / df['PS_RRC_Denum_M']).replace([float('inf'), -float('inf')], 0) * 100
    df['CS RAB SR'] = (df['CS_RAB_Num_M'] / df['CS_RAB_Denum_M']).replace([float('inf'), -float('inf')], 0) * 100
    df['PS RAB SR'] = (df['PS_RAB_Num_M'] / df['PS_RAB_Denum_M']).replace([float('inf'), -float('inf')], 0) * 100
    df['CS DCR'] = (df['CSDROPNOM_C'] / df['CSDROPDENOM_C']).replace([float('inf'), -float('inf')], 0) * 100
    df['HS DCR'] = (df['HSDROP_NUM_V'] / df['HSDROP_DENOM_V']).replace([float('inf'), -float('inf')], 0) * 100
    return df

# Button to Process File
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()  # Ensure no leading/trailing spaces in column names
    st.write("Columns in uploaded file:", df.columns)  # Debug: Print column names
    
    # Check if required columns exist
    missing_columns = [col for col in ['RNC name', 'WCEL name', 'Date'] if col not in df.columns]
    if missing_columns:
        st.error(f"Missing columns: {', '.join(missing_columns)}")
    else:
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
