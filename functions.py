import io
import pandas as pd

from fpdf import FPDF
from pymongo import MongoClient
from collections import defaultdict


def create_entity_shares_data(entities: list[str], substances: list[str], shares: defaultdict):
    total_shares = 0
    entity_shares = []
    
    for entity in entities:
        share = 0
        
        for substance in substances:
            share += shares[entity][substance]
        
        entity_shares.append(share)
        total_shares += share

    for index, entity in enumerate(entity_shares):
        if total_shares > 0:
            entity_shares[index] = entity / total_shares

    entity_shares_data = {
        'Entities': entities,
        'Shares': entity_shares,
    }
    
    return pd.DataFrame(entity_shares_data)


def create_substance_shares_data(entities: list[str], substances: list[str], shares: defaultdict):
    total_shares = 0
    substance_shares = []
    
    for substance in substances:
        share = 0
        
        for entity in entities:
            share += shares[entity][substance]
        
        substance_shares.append(share)
        total_shares += share

    for index, entity in enumerate(substance_shares):
        if total_shares > 0:
            substance_shares[index] = entity / total_shares

    substance_shares_data = {
        'Shares': substance_shares,
        'Substances': substances,
    }
    
    return pd.DataFrame(substance_shares_data)


def export_to_csv(dataframe: pd.DataFrame):
    return dataframe.to_csv(index=False, sep=';')


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
    