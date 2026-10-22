import json
from elasticsearch import Elasticsearch, helpers
import csv
import re
from get_umls import *

es = Elasticsearch("http://localhost:9200")

def index_data(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        drugs = json.load(f)

    actions = [
        {
            "_index": "drugbank",
            "_id": idx,
            "_source": drug
        }
        for idx, drug in enumerate(drugs, start=1)
    ]

    helpers.bulk(es, actions)
    print(f"Indexé {len(drugs)} documents dans Elasticsearch.")

############################
#1st Method : DRUGBANK 
############################

def find_treatment_drugs_es(keyword_str):
    keyword = keyword_str.strip()
    if not keyword:
        print("Aucun mot-clé fourni.")
        return set()

    has_wildcard = "*" in keyword or "?" in keyword

    if has_wildcard:
        query = {
            "size": 1000,
            "query": {
                "query_string": {
                    "query": keyword, 
                    "fields": ["indication"],
                    "default_operator": "AND"
                }
            }
        }
    else:
        query = {
            "size": 1000,
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["indication"],
                    
                }
            }
        }

    response = es.search(index="drugbank", body=query)

    found_drugs = set()
    for hit in response['hits']['hits']:
        found_drugs.add(hit['_source']['name'])

    return found_drugs


def dico_treatment(List_med):
    dico={}
    for e in List_med:
        dico[e]="DRUGBANK"
    return dico 


###########################
#2nd Method SIDER 
###########################

"""
Fisrt step : FIND UMLS_code 
"""
symptom="headache"
umls_codes = get_umls_from_elasticsearch(symptom)
#print("-------------UMLS CODES ---------------")
#print(umls_codes)

"""
STEP 2 : FROM UMLS_CODE find CID 
"""

tsv_file = 'data/SIDER/meddra_all_indications.tsv'  

def get_cid_from_umls(tsv_file, umls_List):
    if not umls_List: 
        return []
    cids = []  
    
    with open(tsv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        
        for row in reader:
            if (len(row)<5):
                continue
            for umls_code in umls_List:
                
                stitch_id = row[0]
                umls_side_effect_1 = row[1]  
                umls_side_effect_2 = row[5]
                if umls_side_effect_1 == umls_code or umls_side_effect_2 == umls_code:
                    cids.append(stitch_id)  
    return list(set(cids)) if cids else None


#print("---------"*10)
#print(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch(symptom)))
##print("---------"*10)



"""
STEP 3 : Convert CID to CIDm + search ATC code with chemical.tsv
"""


# Fichier STITCH
stitch_file = "data/STITCH - ATC/chemical.sources.v5.0.tsv"


def convert_CIDM(List_Cid):
    if not List_Cid:
        return []
    List_CIDM=[]
    for cid in List_Cid: 
        numeric_part = int(cid[3:]) - 100000000  
        stitch_id = f"CIDm{numeric_part:08d}" 
        List_CIDM.append(stitch_id)
    return List_CIDM


#print("--------"*10)
#print(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch(symptom))))
#print("--------"*10)

#Thanks to CIDm find ATC code with chemical.tsv 

def get_atc_by_cidm(cidm_codes, index_name="chemical_index"):
    atc_codes=[]
    for cidm_code in cidm_codes:
        es = Elasticsearch("http://localhost:9200")

        query = {
            "query": {
                "match": { "cidm": cidm_code } 
            }, 
            "size":1000
        }

        response = es.search(index=index_name, body=query)

        atc_code = [hit["_source"]["atc"] for hit in response["hits"]["hits"]]
        if atc_code!=[]:
            for e in atc_code:
                atc_codes.append(e)
    return atc_codes


def remove_duplicates(strings_list):
    return list(set(strings_list))

atc_codes = get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch(symptom))))
#print(atc_codes)



"""
STEP 4 : Find drug name from atc code List
"""




def get_drug_by_atc(file_path, atc_codes):
    drugs=[]
   
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith('E'):
            match = re.match(r"\s*E\s+([A-Za-z0-9]+)\s+(.*)", line)
            if match:
                code = match.group(1)
                drug_name = match.group(2).strip()
                drug_name_clean = re.sub(r'\s*\[.*\]', '', drug_name)
                #drug = concatSource(drug_name_clean, "STITCH")
                if code in atc_codes:
                    drugs.append(drug_name_clean)

    return drugs


file_path = 'data/STITCH - ATC/br08303.keg'


#print(get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch(symptom)))) ))
#print(len(get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch("headache")))) )))
#print(len(get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch("stomach ache")))) )))

"""
print("-"*50)
print("STITCH")
print("-"*50)
print(get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch("headache")))) ))
"""



def search_treatment_final(symptom):
    List_STITCH = get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch(symptom)))))
    List_DRUGBANK = find_treatment_drugs_es(symptom)
    
    element_source = {}

    for e in List_STITCH:
        element_source[e] = "STITCH"

    for e in List_DRUGBANK:
        if e in element_source:
            element_source[e] = "STITCH + DRUGBANK"
        else:
            element_source[e] = "DRUGBANK"

    return element_source 



#print("*"*10)
#print(search_treatment_final("headache"))


####STATS DRUGBANK / STITCH / STICTH + DRUGBANK : 

def count_sources_SE2(dico_drugs):
    drugbank = 0
    stitch = 0 
    drug_and_stitch = 0 
    L=[]
    for key in dico_drugs:
        if dico_drugs[key]=="STITCH":
            stitch+=1
        elif dico_drugs[key]=="DRUGBANK":
            drugbank+=1
        elif dico_drugs[key]=="DRUGBANK + STITCH" or dico_drugs[key]=="STITCH + DRUGBANK":
            drug_and_stitch+=1
    L.append(stitch)
    L.append(drugbank)
    L.append(drug_and_stitch)
    return L 

#print(count_sources_SE(search_treatment_final(symptom)))


def sort_dico_drugs2(dico_drugs):
    priority_order = {"STITCH + DRUGBANK": 1,"DRUGBANK + STITCH":1, "STITCH": 2, "DRUGBANK": 3}
    sorted_dico = dict(sorted(dico_drugs.items(), key=lambda item: priority_order.get(item[1], 4)))
    return sorted_dico
