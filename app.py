import os
import pandas as pd
import streamlit as st
import plotly.express as px

from utils import *
from enum import Enum
from dotenv import load_dotenv
from pymongo import MongoClient
from collections import defaultdict


class Format(Enum):
    CSV = 'CSV'
    Excel = 'Excel'
    PDF = 'PDF'


load_dotenv()

COLLECTION_NAME = os.getenv('COLLECTION_NAME')
DATABASE_NAME = os.getenv('DATABASE_NAME')
MONGODB_URI = os.getenv('MONGODB_URI')

st.set_page_config(page_title="TASS", page_icon="💬")
st.title('💊 Reimbursed Medicines Analysis')
st.write('Welcome to the application that allows analysis of reimbursed medicines in Poland!')

# --- Input Section ---
st.header('Input Parameters')

try:
    client = MongoClient(MONGODB_URI)

except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

data = fetch_data(client, DATABASE_NAME, COLLECTION_NAME)

entities = set()
substances = set()
medicines = defaultdict(list)
shares = defaultdict(lambda: defaultdict(int))

for item in data:
    substances.add(item['substance'])
    medicines[item['substance']].append(item['drug'])
    manufacturer = item['manufacturer']

    if isinstance(manufacturer, str):
        entities.add(manufacturer)
        shares[item['manufacturer']][item['substance']] += item['reimbursement']

substances = list(substances)
entities = list(entities)

# Active Substances selection
selected_substances = st.multiselect('Select active substances:', substances)

# Responsible Entities selection
selected_entities = st.multiselect('Select responsible entities:', entities)

# Filter medicines based on selected substances
filtered_medicines = []

for substance in selected_substances:
    filtered_medicines.extend(medicines[substance])

filtered_medicines = list(set(filtered_medicines))  # Remove duplicates

# --- Medicines List ---
st.subheader('Medicines List')

if filtered_medicines:
    with st.expander('Medicines List', expanded=False):
        for med in filtered_medicines:
            st.write(f'- {med}')

else:
    st.write('No medicines selected.')

# --- Shares Table ---
st.subheader('Shares Table')
shares_data = []
df_shares = pd.DataFrame()

for entity in selected_entities:
    for substance in selected_substances:
        shares_data.append({'Entity': entity, 'Substance': substance, 'Share': shares[entity][substance]})

if shares_data:
    df_shares = pd.DataFrame(shares_data)
    st.dataframe(df_shares)

else:
    st.write('No data to display for selected entities and substances.')

# --- Visualizations Section ---
st.subheader('Visualizations')

if not df_shares.empty:
    df_entity_shares = create_entity_shares_data(selected_entities, selected_substances, shares)
    df_substance_shares = create_substance_shares_data(selected_entities, selected_substances, shares)

    if df_entity_shares.empty or df_substance_shares.empty:
        st.write('No data to display for selected entities and substances.')
    
    else: 
        entities_fig = px.pie(df_entity_shares, names='Entities', values='Shares', title='Entity share in reimbursments')
        entities_fig.update_layout(legend=dict(font=dict(size=8), itemwidth=30))
        st.plotly_chart(entities_fig)

        substances_fig = px.pie(df_substance_shares, names='Substances', values='Shares', title='Substance share in reimbursments')
        substances_fig.update_layout(legend=dict(font=dict(size=8), itemwidth=30))
        st.plotly_chart(substances_fig)

else:
    st.write('No data to display for selected entities and substances.')

with st.expander('Export Data', expanded=False):
    # Data Export format selection
    selected_format = st.selectbox('_', [f.value for f in Format], key='format_select', 
                                   disabled=df_shares.empty, label_visibility="collapsed", 
                                   index=None, placeholder="Select export format...")

    # --- Export Button ---
    match selected_format:
        case Format.CSV.value:
            csv_data = export_to_csv(df_shares)
                
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="shares_table.csv",
                mime="text/csv"
            )
        case Format.Excel.value:
            buffer = export_to_excel(df_shares)
            
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name="tass-shares.xlsx",
                mime="application/vnd.ms-excel",
            )
        case Format.PDF.value:
            pdf = export_to_pdf(df_shares)

            st.download_button(
                label="Download PDF",
                data=bytes(pdf.output()),
                file_name="tass-shares.pdf",
                mime="application/pdf",
            )
        case _:
            pass
