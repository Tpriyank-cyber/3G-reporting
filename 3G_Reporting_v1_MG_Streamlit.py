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

# Function for Data Processing
def process_data(uploaded_file, sheet_type):
    df = pd.read_excel(uploaded_file)
    df['Start Time'] = pd.to_datetime(df['Period start time'])
    df["Date"] = df["Period start time"].dt.date
    df = calculate_kpis(df)

    # Selecting Processing Type
    if sheet_type == "BBH":
        pivot = pd.pivot_table(df, index=['RNC name', 'WBTS name'], columns='Date', values=KPI_Obj, aggfunc='sum')
        output_filename = "3G_Day_Site_Level_KPIs_output.xlsx"
    else:
        pivot = pd.pivot_table(df, index=['RNC name', 'WCEL name'], columns='Date', values=KPI_Obj, aggfunc='sum')
        output_filename = "3G_Day_Cell_Level_KPIs_output.xlsx"

    pivot = pivot.stack(level=0).reset_index(drop=False)
    pivot.rename(columns={'level_1': 'KPI NAME'}, inplace=True)

    return pivot, output_filename

# Button to Process File
if uploaded_file:
    if st.button("🔄 Process Data"):
        processed_df, output_filename = process_data(uploaded_file, sheet_type)

        # Convert to Excel for Download
        @st.cache_data
        def convert_df_to_excel(df):
            output = pd.ExcelWriter(output_filename, engine='xlsxwriter')
            df.to_excel(output, index=False, sheet_name="Processed Data")
            output.close()
            return output_filename

        st.success("✅ Data Processed Successfully!")
        st.dataframe(processed_df.head())  # Show processed data preview

        # Download Button
        with open(output_filename, "rb") as file:
            st.download_button(label="⬇️ Download Processed File", data=file, file_name=output_filename)
