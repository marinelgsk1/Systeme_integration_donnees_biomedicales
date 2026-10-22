import csv
from elasticsearch import Elasticsearch
from get_umls import *
from sider_to_stitch import *

sider_tsv_path="data\SIDER\\meddra_all_se.tsv"
def convert_CIDM(cid):
    """
    Converts a long STITCH ID to a CIDm format.
    """
    numeric_part = int(cid[3:]) - 100000000  
    stitch_id = f"CIDm{numeric_part:08d}"  
    return stitch_id


def find_cids_in_sider(umls_code, sider_tsv_path="data/SIDER/meddra_all_se.tsv"):
    
    cids = []
    with open(sider_tsv_path, mode='r', encoding='utf-8') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        for row in reader:
            if len(row) < 5:
                continue
            
            stitch_id_long = row[0]      
            umls_side_effect_1 = row[2] 
            umls_side_effect_2 = row[4] 

            if umls_side_effect_1 == umls_code or umls_side_effect_2 == umls_code:
                cids.append(stitch_id_long)

    return cids


def retrieve_medications_for_symptom(symptom, sider_tsv_path):
    umls_codes = get_umls_from_elasticsearch(symptom)
    all_cids = []
    for umls_code in umls_codes:
        cids_found = find_cids_in_sider(umls_code, sider_tsv_path)
        all_cids.extend(cids_found)
    cidms = [convert_CIDM(cid) for cid in all_cids]
    all_atc_codes = []
    for cidm in cidms:
        atc_codes_for_cidm = search_atc_by_cidm(cidm)
        all_atc_codes.extend(atc_codes_for_cidm)
    all_atc_codes = list(set(all_atc_codes))
    return all_atc_codes

if __name__ == "__main__":
    symptom = "stomach ache"
   
    

    #atc_codes = retrieve_medications_for_symptom(symptom, sider_tsv_path)

    #if atc_codes:
       # print(f"Pour le symptôme '{symptom}', voici les codes ATC trouvés :")
       # print(len(atc_codes))
    #else:
       # print(f"Aucun médicament trouvé pour le symptôme '{symptom}'.")