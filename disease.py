import sqlite3
import re

def clean_disease_name(disease_label):
    """
    Cleans the disease name by:
    1) Removing special characters (#, %) and any leading numbers.
    2) Extracting only the part before the first semicolon ';' 
       to ignore synonyms or extra info.
    Examples:
      - "#604187 SPASTIC PARAPLEGIA 10, AUTOSOMAL DOMINANT; SPG10" 
         -> "SPASTIC PARAPLEGIA 10, AUTOSOMAL DOMINANT"
      - "%608703 SPINOCEREBELLAR ATAXIA 25; SCA25" 
         -> "SPINOCEREBELLAR ATAXIA 25"
    """
    # 1) Remove special chars (#, %) + leading numbers
    cleaned = re.sub(r"^[#%]?\d+\s*", "", disease_label).strip()
    # 2) Take only the substring before the first ';'
    main_part = cleaned.split(";")[0].strip()
    return main_part

def get_diseases_for_hpo(hpo_id, db_path="data/HPO/hpo_annotations.sqlite"):
   
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Adjust table and column names if needed
    query = """
    SELECT disease_db, disease_id, disease_label
    FROM phenotype_annotation
    WHERE sign_id = ?
    """
    cursor.execute(query, (hpo_id,))

    rows = cursor.fetchall()
    conn.close()

    # Convert each row into a dictionary
    disease_names = [clean_disease_name(row[2]) for row in rows]
    return disease_names


#print(get_diseases_for_hpo("HP:0012199", db_path="data/HPO/hpo_annotations.sqlite"))

import sqlite3

def get_sources_for_disease(disease_name, db_path="data/HPO/hpo_annotations.sqlite"):
   
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT DISTINCT disease_db 
    FROM phenotype_annotation
    WHERE disease_label = ?
    """
    cursor.execute(query, (disease_name,))  # Recherche exacte

    sources = [row[0] for row in cursor.fetchall()]
    conn.close()

    return sources

#print(get_sources_for_disease("CLUSTER HEADACHE, FAMILIAL"))


def dico_disease(symptom, db_path="data/HPO/hpo_annotations.sqlite"):
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT DISTINCT disease_label, disease_db
    FROM phenotype_annotation
    WHERE sign_id = ?
    """
    cursor.execute(query, (symptom,))


    disease_dict = {clean_disease_name(row[0]): row[1] for row in cursor.fetchall()}

    conn.close()
    return disease_dict


#print(dico_disease("HP:0004233"))


