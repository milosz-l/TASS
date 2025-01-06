import pandas as pd
import streamlit as st

from pymongo import MongoClient
from collections import defaultdict


def export_to_csv(dataframe):
    csv = dataframe.to_csv()
    
    return csv


def export_to_excel(dataframe, output_path="shares_table.xlsx"):
    dataframe.to_excel(output_path, index=False)
    
    return output_path


def fetch_data(client, db_name, collection_name, query=None):
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
    formats = ['CSV', 'Excel', 'PDF']
    selected_format = st.selectbox('Select export format:', formats, key='format_select')

    # --- Export Button ---
    if not df_shares.empty:
        if selected_format == 'CSV':
            csv_data = export_to_csv(df_shares)
            
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="shares_table.csv",
                mime="text/csv"
            )

        else:
            if st.button("Download Excel"):
                excel_path = export_to_excel(df_shares)
