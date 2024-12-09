import streamlit as st
import pandas as pd

st.title('💊 Reimbursed Medicines Analysis')
st.write('Welcome to the application that allows analysis of reimbursed medicines in Poland!')

# --- Input Section ---
st.header('Input Parameters')

# Sample data for substances and medicines
substances = ['Paracetamol', 'Ibuprofen', 'Amoxicillin', 'Cetrizine', 'Loratadine']
medicines = {
    'Paracetamol': ['Tylenol', 'Panadol', 'Paracete'],
    'Ibuprofen': ['Advil', 'Nurofen', 'Ibu'],
    'Amoxicillin': ['Amoxil', 'Moxatag', 'Trimox'],
    'Cetrizine': ['Zyrtec', 'Reactine', 'Cetirizine'],
    'Loratadine': ['Claritin', 'Alavert', 'Loratadine']
}

# Sample data for entities and shares
entities = ['Entity A', 'Entity B', 'Entity C', 'Entity D', 'Entity E']
shares = {
    'Entity A': {'Paracetamol': '25%', 'Ibuprofen': '15%', 'Amoxicillin': '30%', 'Cetrizine': '20%', 'Loratadine': '10%'},
    'Entity B': {'Paracetamol': '10%', 'Ibuprofen': '40%', 'Amoxicillin': '15%', 'Cetrizine': '30%', 'Loratadine': '5%'},
    'Entity C': {'Paracetamol': '35%', 'Ibuprofen': '20%', 'Amoxicillin': '25%', 'Cetrizine': '15%', 'Loratadine': '35%'},
    'Entity D': {'Paracetamol': '15%', 'Ibuprofen': '10%', 'Amoxicillin': '15%', 'Cetrizine': '20%', 'Loratadine': '25%'},
    'Entity E': {'Paracetamol': '15%', 'Ibuprofen': '15%', 'Amoxicillin': '15%', 'Cetrizine': '15%', 'Loratadine': '25%'}
}

# Active Substances selection
selected_substances = st.multiselect('Select active substances:', substances, default=['Paracetamol'])

# Responsible Entities selection
selected_entities = st.multiselect('Select responsible entities:', entities, default=['Entity A'])



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
    if st.button('Export'):
        st.success(f'Data has been exported in {selected_format} format.')
        # Add the data export function here