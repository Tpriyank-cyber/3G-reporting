import streamlit as st
import pandas as pd

# Streamlit App Title
st.title("📊 3G KPI Data Processing Tool")

# Upload file
uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read the file and show sheet names
    df_dict = pd.read_excel(uploaded_file, sheet_name=None)  # Read all sheets
    sheet_names = list(df_dict.keys())  # Get available sheet names
    
    # Select a sheet to process
    selected_sheet = st.selectbox("Select the sheet to process:", sheet_names)

    # Read the selected sheet
    df = df_dict[selected_sheet]
    
    # Trim column names (removes extra spaces)
    df.columns = df.columns.str.strip()

    # Display available columns for debugging
    st.write("📋 Available Columns:", df.columns.tolist())

    # Verify that 'Period start time' exists
    if 'Period start time' not in df.columns:
        st.error("❌ 'Period start time' column not found. Please check the file and upload again.")
    else:
        st.success("✅ 'Period start time' column found. Processing can proceed.")

        # Select processing type (Daily or Hourly)
        processing_type = st.selectbox("Select processing type:", ["Daily", "Hourly"])

        # Hour Selection (Only if "Hourly" is selected)
        hour_input = None
        if processing_type == "Hourly":
            hour_input = st.selectbox("Select Hour for Processing:", list(range(0, 24)))

        # Define KPI Columns
        KPI_Obj = [
            'CS RRC SR', 'PS RRC SR', 'CS RAB SR', 'PS RAB SR', 'CS DCR', 'HS DCR',
            'Act HS-DSCH end usr thp', 'CellAvailabilityexcluding', 'CS Traffic',
            'Inter sys RT Hard HO SR', 'Max simult HSDPA users', 'PS Traffic',
            'SHO_SR_M', 'Average RTWP'
        ]

        # Function to calculate KPIs
        def calculate_kpis(df):
            df['CS RRC SR'] = df.apply(lambda x: (x.get('CS_RRC_Num_M', 0) / x.get('CS_RRC_Denum_M', 1)) * 100, axis=1)
            df['PS RRC SR'] = df.apply(lambda x: (x.get('PS_RRC_Num_M', 0) / x.get('PS_RRC_Denum_M', 1)) * 100, axis=1)
            df['CS RAB SR'] = df.apply(lambda x: (x.get('CS_RAB_Num_M', 0) / x.get('CS_RAB_Denum_M', 1)) * 100, axis=1)
            df['PS RAB SR'] = df.apply(lambda x: (x.get('PS_RAB_Num_M', 0) / x.get('PS_RAB_Denum_M', 1)) * 100, axis=1)
            df['CS DCR'] = df.apply(lambda x: (x.get('CSDROPNOM_C', 0) / x.get('CSDROPDENOM_C', 1)) * 100, axis=1)
            df['HS DCR'] = df.apply(lambda x: (x.get('HSDROP_NUM_V', 0) / x.get('HSDROP_DENOM_V', 1)) * 100, axis=1)
            return df

        # Function for Data Processing
        def process_data(df, processing_type, hour_input):
            df['Start Time'] = pd.to_datetime(df['Period start time'], errors='coerce')
            df["Date"] = df["Start Time"].dt.date
            df["Hour"] = df["Start Time"].dt.hour
            df = calculate_kpis(df)

            if processing_type == "Daily":
                pivot = pd.pivot_table(df, index=['RNC name', 'WBTS name'], columns='Date', values=KPI_Obj, aggfunc='sum')
                output_filename = "3G_Day_Site_Level_KPIs_output.xlsx"
            else:  # Hourly Processing
                if hour_input is not None:
                    df = df[df["Hour"] == hour_input]  # Filter for selected hour
                pivot = pd.pivot_table(df, index=['RNC name', 'WCEL name'], columns=['Date', 'Hour'], values=KPI_Obj, aggfunc='sum')
                output_filename = "3G_Hourly_Cell_Level_KPIs_output.xlsx"

            pivot = pivot.stack(level=0).reset_index(drop=False)
            pivot.rename(columns={'level_1': 'KPI NAME'}, inplace=True)

            return pivot, output_filename

        # Button to Process File
        if st.button("🔄 Process Data"):
            processed_df, output_filename = process_data(df, processing_type, hour_input)

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
