import random
import numpy as np
import pandas as pd
import networkx as nx


file_path_1 = "1.xlsx"
file_path_2 = "2.xlsx"
file_path_3 = "rejestr.xlsx"

df1_A1 = pd.read_excel(file_path_1, skiprows=2, sheet_name="A1")
df1_A2 = pd.read_excel(file_path_1, skiprows=1, sheet_name="A2")
df1_A3 = pd.read_excel(file_path_1, skiprows=1, sheet_name="A3")
df1_B = pd.read_excel(file_path_1, skiprows=1, sheet_name="B")
df1_C = pd.read_excel(file_path_1, skiprows=1, sheet_name="C")
df1_D = pd.read_excel(file_path_1, skiprows=1, sheet_name="D")

df2_A1 = pd.read_excel(file_path_2, sheet_name="A1")
df2_A2 = pd.read_excel(file_path_2, sheet_name="A2")
df2_A3 = pd.read_excel(file_path_2, sheet_name="A3")

manufacturer_df = pd.read_excel(file_path_3, sheet_name="Lista Produktow Leczniczych")

df1_A1["Producent"] = "Unknown"
df1_A2["Producent"] = "Unknown"
df1_A3["Producent"] = "Unknown"
df1_B["Producent"] = "Unknown"
df1_C["Producent"] = "Unknown"
df1_D["Producent"] = "Unknown"

for col in ["Cena detaliczna", "Cena hurtowa brutto", "Wysokość dopłaty świadczeniobiorcy"]:
    if col in df1_A1.columns:  
        df1_A1[col] = df1_A1[col].apply(lambda x: int(str(x).replace(",", "")))
    
    if col in df1_A2.columns:  
        df1_A2[col] = df1_A2[col].apply(lambda x: int(str(x).replace(",", "")))

    if col in df1_A3.columns:   
        df1_A3[col] = df1_A3[col].apply(lambda x: int(str(x).replace(",", "")))

    if col in df1_B.columns:
        df1_B[col] = df1_B[col].apply(lambda x: int(str(x).replace(",", "")))

    if col in df1_C.columns:   
        df1_C[col] = df1_C[col].apply(lambda x: int(str(x).replace(",", "")))

    if col in df1_D.columns:   
        df1_D[col] = df1_D[col].apply(lambda x: int(str(x).replace(",", "")))

title_A1 = pd.read_excel(file_path_1, nrows=1, sheet_name="A1").iloc[0, 0]
title_A2 = pd.read_excel(file_path_1, header=None, nrows=1, sheet_name="A2").iloc[0, 0]
title_A3 = pd.read_excel(file_path_1, header=None, nrows=1, sheet_name="A3").iloc[0, 0]
title_B = pd.read_excel(file_path_1, header=None, nrows=1, sheet_name="B").iloc[0, 0]
title_C = pd.read_excel(file_path_1, header=None, nrows=1, sheet_name="C").iloc[0, 0]
title_D = pd.read_excel(file_path_1, header=None, nrows=1, sheet_name="D").iloc[0, 0]

G = nx.Graph()
df = df1_A1.copy()

for _, row in df.iterrows():
    substance = row["Substancja czynna"]
    reimbursement = None
    drug = None
    
    for lbl in ["Nazwa  postać i dawka", "Nazwa  postać i dawka leku"]:
        if lbl in df.columns:
            drug = row[lbl]
            break

    ean_code = row["Kod EAN lub inny kod odpowiadający kodowi EAN"]

    if not "Cena detaliczna" in df.columns:
        if not "Cena hurtowa brutto" in df.columns:
            reimbursement = df1_A1.loc[df1_A1["Kod EAN lub inny kod odpowiadający kodowi EAN"] == ean_code, "Cena detaliczna"].iloc[0]
        
        else:
            reimbursement = row["Cena hurtowa brutto"] - row["Wysokość dopłaty świadczeniobiorcy"]
    else:
        reimbursement = row["Cena detaliczna"] - row["Wysokość dopłaty świadczeniobiorcy"]

    if substance not in G:
        G.add_node(substance, type="substance")
    
    if drug not in G:
        manufacturer = df2_A1.loc[df2_A1["ean"] == ean_code, "producent"]

        if not manufacturer.empty and manufacturer.iloc[0] != "nan":
            manufacturer = manufacturer.iloc[0]
        else:
            manufacturer = "Unknown"

        if manufacturer == "Unknown":
            manufacturer1 = manufacturer_df.loc[manufacturer_df["Opakowanie"].str.contains(str(ean_code), na=False), "Nazwa wytwórcy"]
            manufacturer2 = manufacturer_df.loc[manufacturer_df["Opakowanie"].str.contains(str(ean_code), na=False), "Nazwa wytwórcy/importera"]

            if not manufacturer1.empty:
                manufacturer = manufacturer1.iloc[0]
            
            elif not manufacturer2.empty:
                manufacturer = manufacturer2.iloc[0]

        G.add_node(drug, type="drug", ean=ean_code, manufacturer=manufacturer)
    
    if not G.has_edge(substance, drug):
        G.add_edge(substance, drug, weight=reimbursement)

unique_substances = list(set([node for node, data in G.nodes(data=True) if data.get("type") == "substance"]))
substance_groups = {}

for substance in unique_substances:
    total_reimbursement = 0
    reimbursement_per_drug = {}

    for drug in list(G.neighbors(substance)):
        if G.has_edge(substance, drug):
            reimbursement = G[substance][drug].get("weight", 0)
            total_reimbursement += reimbursement
            reimbursement_per_drug[drug] = (G.nodes[drug].get("manufacturer", "Unknown"), reimbursement)
    
    substance_groups[substance] = {
        "total_reimbursement": total_reimbursement,
        "reimbursement_per_drug": reimbursement_per_drug
    }

for k1, v1 in substance_groups.items():
    print("-----------------------------------------------------------------------------")
    print(k1, "\nTotal reimbursement =", v1["total_reimbursement"] / 100, "PLN")
    print("\nReimbursement per drug:")

    for k2, v2 in v1["reimbursement_per_drug"].items():
        print(v2[0], "|", k2, "=", v2[1] / 100, "PLN")
    
    print("-----------------------------------------------------------------------------\n")


############################################################

g_loops = nx.number_of_selfloops(G)
g_nodes = nx.number_of_nodes(G)
g_edges = nx.number_of_edges(G)

print("------------------------------------------")
print("Właściwości grafu:")
print("Pętle:", g_loops)
print("Rząd:", g_nodes)
print("Rozmiar:", g_edges)
print("------------------------------------------")

############################################################

if not nx.is_connected(G):
    largest_component = max(list(nx.connected_components(G)))
    G = G.subgraph(largest_component)

g_nodes = nx.number_of_nodes(G)
g_edges = nx.number_of_edges(G)

print("\n------------------------------------------")
print("Największa składowa spójna grafu:")
print("Rząd:", g_nodes)
print("Rozmiar:", g_edges)
print("------------------------------------------")

############################################################

seed = 0
sample_sizes = [100, 1000, 10000]

random.seed(seed)
np.random.seed(seed)

results = {}
nodes = list(G.nodes())
n = len(nodes)
print("\n------------------------------------------")
print("Aproksymacja średniej długości ścieżki:")

for sample_size in sample_sizes:
    path_lengths = []

    source_nodes = np.random.choice(nodes, sample_size, replace=True)
    target_nodes = np.random.choice(nodes, sample_size, replace=True)

    for source, target in zip(source_nodes, target_nodes):
        if source != target:
            try:
                length = nx.shortest_path_length(G, source, target)
                path_lengths.append(length)
            except nx.NetworkXNoPath:
                continue

    avg_length = np.mean(path_lengths)
    std_dev = np.std(path_lengths)

    results[sample_size] = {"Liczba par wierzchołków:": len(path_lengths),
                            "Średnia długość:": avg_length,
                            "Odchylenie standardowe:": std_dev}

print("------------------------------------------")

for key in results.keys():
    for k, v in results[key].items():
        print(k, v)

    print("------------------------------------------")
