import os
import pandas as pd

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

COLLECTION_NAME = os.getenv('COLLECTION_NAME')
DATABASE_NAME = os.getenv('DATABASE_NAME')
MONGODB_URI = os.getenv('MONGODB_URI')

def load_excel(file_path: str, skip_rows: int, sheet_name: str):
    return pd.read_excel(file_path, skiprows=skip_rows, sheet_name=sheet_name)

def prepare_data(sheet_dfs: list[pd.DataFrame], manufacturer_df: pd.DataFrame):
  data = list()

  for df in sheet_dfs:
    for _, row in df.iterrows():
        substance = row["Substancja czynna"]
        reimbursement = None
        drug = None
        manufacturer = None
        
        for lbl in ["Nazwa  postać i dawka", "Nazwa  postać i dawka leku"]:
            if lbl in df.columns:
                drug = row[lbl]
                break

        ean_code = row["Kod EAN lub inny kod odpowiadający kodowi EAN"]

        if not "Cena detaliczna" in df.columns:
            if not "Cena hurtowa brutto" in df.columns:
                reimbursement = sheet_dfs[0].loc[sheet_dfs[0]["Kod EAN lub inny kod odpowiadający kodowi EAN"] == ean_code, "Cena detaliczna"].iloc[0]
            
            else:
                reimbursement = row["Cena hurtowa brutto"] - row["Wysokość dopłaty świadczeniobiorcy"]
        
        else:
            reimbursement = row["Cena detaliczna"] - row["Wysokość dopłaty świadczeniobiorcy"]

        manufacturer_columns = ["Nazwa wytwórcy", "Nazwa wytwórcy/importera"]

        for col in manufacturer_columns:
            if manufacturer != None:
                continue

            manufacturers = manufacturer_df.loc[manufacturer_df["Opakowanie"].str.contains(str(ean_code), na=False), col]
            
            if not manufacturers.empty:
                manufacturer = manufacturers.iloc[0]

        if (manufacturer != None):
            data.append({
                "drug": drug,
                "ean": ean_code,
                "manufacturer": manufacturer,
                "reimbursement": reimbursement / 100,
                "substance": substance,
            })

  return data

def connect_to_mongodb(uri: str):
    try:
        client = MongoClient(uri)
        print("Connected to MongoDB!")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def insert_data(client: MongoClient, db_name: str, collection_name: str, data: list):
    try:
        db = client[db_name]
        collection = db[collection_name]

        if isinstance(data, list):
            result = collection.insert_many(data)
            print(f"Inserted {len(result.inserted_ids)} documents into {collection_name}.")
            return result.inserted_ids

    except Exception as e:
        print(f"Error inserting data: {e}")
        return None

if __name__ == "__main__":
    client = connect_to_mongodb(uri=MONGODB_URI)
    if not client:
        exit()

    sheet_dfs = []
    main_filename = "1.xlsx"
    manufacturer_filename = "rejestr.xlsx"

    sheets = [
        {"skip_rows": 2, "sheet_name": "A1" },
        {"skip_rows": 1, "sheet_name": "A2" },
        {"skip_rows": 1, "sheet_name": "A3" },
        {"skip_rows": 1, "sheet_name": "B" },
        {"skip_rows": 1, "sheet_name": "C" },
        {"skip_rows": 1, "sheet_name": "D" },
    ]

    for sheet in sheets:
      excel_data = load_excel(main_filename, skip_rows=sheet["skip_rows"], sheet_name=sheet["sheet_name"])
      sheet_dfs.append(excel_data)

    for col in ["Cena detaliczna", "Cena hurtowa brutto", "Wysokość dopłaty świadczeniobiorcy"]:
        for df in sheet_dfs:
            if col in df.columns:  
                df[col] = df[col].apply(lambda x: int(str(x).replace(",", "")))

    manufacturer_df = pd.read_excel(manufacturer_filename, 
                                  usecols=["Opakowanie", "Nazwa wytwórcy", "Nazwa wytwórcy/importera"], 
                                  sheet_name="Lista Produktow Leczniczych")

    mongo_data = prepare_data(sheet_dfs, manufacturer_df)

    insert_data(client, DATABASE_NAME, COLLECTION_NAME, mongo_data)

    client.close()