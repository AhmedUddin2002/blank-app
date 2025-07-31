import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="Excel to Cleaned CSV", layout="centered")

st.title("📊 Clean Admission Excel Data")
st.write("Upload the Excel file and download the cleaned CSV file.")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"], accept_multiple_files=False)

if uploaded_file is not None:
    try:
        # Read and clean data
        df_raw = pd.read_excel(uploaded_file, skiprows=4)

        df_raw.columns = [
            'S.No', 'District', 'Institution Name',
            'V Minorities Sanctioned', 'V Minorities Admitted',
            'V NonMinorities Sanctioned', 'V NonMinorities Admitted',
            'Course',
            'Inter Minorities Sanctioned', 'Inter Minorities Admitted',
            'Inter NonMinorities Sanctioned', 'Inter NonMinorities Admitted'
        ]

        # Remove last row
        df_raw = df_raw.iloc[:-1]

        # Clean Institution Name
        df_raw['Institution Name'] = df_raw['Institution Name'].astype(str).apply(
            lambda x: re.sub(r'\([^)]*\)', '', x).replace('Boys', 'B').replace('Girls', 'G').strip()
        )

        # Convert numeric cols
        numeric_cols = [
            'V Minorities Sanctioned', 'V Minorities Admitted',
            'V NonMinorities Sanctioned', 'V NonMinorities Admitted',
            'Inter Minorities Sanctioned', 'Inter Minorities Admitted',
            'Inter NonMinorities Sanctioned', 'Inter NonMinorities Admitted'
        ]
        for col in numeric_cols:
            df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce').fillna(0).astype(int)

        # Process Class V
        df_v = df_raw[['S.No', 'District', 'Institution Name',
                       'V Minorities Sanctioned', 'V Minorities Admitted',
                       'V NonMinorities Sanctioned', 'V NonMinorities Admitted']].copy()
        df_v['Class'] = 'V'
        df_v['Sanctioned'] = df_v['V Minorities Sanctioned'] + df_v['V NonMinorities Sanctioned']
        df_v['Admitted'] = df_v['V Minorities Admitted'] + df_v['V NonMinorities Admitted']

        # Process Inter
        df_inter = df_raw[['S.No', 'District', 'Institution Name',
                           'Inter Minorities Sanctioned', 'Inter Minorities Admitted',
                           'Inter NonMinorities Sanctioned', 'Inter NonMinorities Admitted']].copy()
        df_inter['Class'] = 'Inter 1st Year'
        df_inter['Sanctioned'] = df_inter['Inter Minorities Sanctioned'] + df_inter['Inter NonMinorities Sanctioned']
        df_inter['Admitted'] = df_inter['Inter Minorities Admitted'] + df_inter['Inter NonMinorities Admitted']

        # Combine and calculate
        df_final = pd.concat([df_v, df_inter], ignore_index=True)
        df_final['Vacancies'] = df_final['Sanctioned'] - df_final['Admitted']
        df_final = df_final[['S.No', 'District', 'Institution Name', 'Class', 'Sanctioned', 'Admitted', 'Vacancies']]

        # Download CSV
        csv_buffer = io.StringIO()
        df_final.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        st.success("✅ File processed successfully!")

        st.download_button(
            label="📥 Download Cleaned CSV",
            data=csv_data,
            file_name="cleaned_admission_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
