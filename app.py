from collections import defaultdict
from enum import Enum
from fpdf import FPDF
import io
import pandas as pd
from pymongo import MongoClient
import streamlit as st

class Format(Enum):
    CSV = 'CSV'
    Excel = 'Excel'
    PDF = 'PDF'

def export_to_csv(dataframe: pd.DataFrame):
    csv = dataframe.to_csv(index=False, sep=';')
    
    return csv

def export_to_excel(dataframe: pd.DataFrame):
    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    dataframe.to_excel(writer, index=False)
    writer.close()

    return buffer

def export_to_pdf(dataframe: pd.DataFrame):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVuSans", "", "./DejaVuSans.ttf")
    pdf.add_font("DejaVuSans", "B", "./DejaVuSans-Bold.ttf")
    pdf.set_font("DejaVuSans", size=12)

    pdf.write_html(dataframe.to_html(index=False).replace('<td>', '<td align="center" bgcolor="#D3D3D3">'))
    
    return pdf

def fetch_data(client: MongoClient, db_name: str, collection_name: str, query: dict | None=None):
    try:
        db = client[db_name]
        collection = db[collection_name]
        query = query or {}
        documents = list(collection.find(query))
        
        return documents
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        
        return []


st.set_page_config(page_title="TASS", page_icon="💬", layout="wide")

st.title('💊 Reimbursed Medicines Analysis')
st.write('Welcome to the application that allows analysis of reimbursed medicines in Poland!')

# --- Input Section ---
st.header('Input Parameters')

mongodb_uri = "mongodb+srv://tass-user:IAANHGvQ43hJn0qA@tass.r5pvw.mongodb.net/"

try:
    client = MongoClient(mongodb_uri)
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

database_name = "project-data"
collection_name = "medicines"

data = fetch_data(client, database_name, collection_name)

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

st.write(shares) # FOR TESTS ONLY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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

# --- Visualizations Section ---
st.header('Visualizations')

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

with st.expander('Export Data', expanded=False):
    # Data Export format selection
    selected_format = st.selectbox('', [f.value for f in Format], key='format_select', 
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