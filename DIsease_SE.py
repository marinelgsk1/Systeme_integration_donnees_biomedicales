import csv
from elasticsearch import Elasticsearch
import re
from get_umls import *

########################################
# First Methode : HPO -> SIDER -> STITCH 
########################################

"""
Fisrt step : FIND UMLS_code 
"""

es = Elasticsearch("http://localhost:9200")  

INDEX_NAME = "hpo_index"  

def get_umls_from_elasticsearch2(symptom):
    
   
    query = {
        "query": {
            "bool": {
                "should": [
                    {"match_phrase": {"name": symptom}},  
                    {"match_phrase": {"synonyms": symptom}}  
                ]
            }
        }
    }
    response = es.search(index=INDEX_NAME, body=query)

    umls_codes = []
    for hit in response["hits"]["hits"]:
        if "umls" in hit["_source"]: 
            umls_codes.extend(hit["_source"]["umls"])  

    return list(set(umls_codes))  

symptom_name = "headache" 

"""
print("-------UMLS_CODE--------")
 
umls_codes = get_umls_from_elasticsearch(symptom_name)
print(umls_codes)
print("---------------")
"""

"""
STEP 2 : FROM UMLS_CODE find CID 
"""

tsv_file = 'data/SIDER/meddra_all_se.tsv'  


#print(find_cids_in_sider(get_umls_from_elasticsearch(symptom_name), tsv_file))

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
                umls_side_effect_1 = row[2]  
                umls_side_effect_2 = row[4]
                if umls_side_effect_1 == umls_code or umls_side_effect_2 == umls_code:
                    cids.append(stitch_id)  
    return list(set(cids)) 



#print(len(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch(symptom_name))))


"""
STEP 3 : Convert CID to CIDm + search ATC code with chemical.tsv
"""


# Fichier STITCH
stitch_file = "data/STITCH - ATC/chemical.sources.v5.0.tsv"


def convert_CIDM(List_Cid):
    if not List_Cid:
        return []

    List_CIDM = []
    for cid in List_Cid: 
        numeric_part = int(cid[3:]) - 100000000  
        stitch_id = f"CIDm{numeric_part:08d}" 
        List_CIDM.append(stitch_id)
    return List_CIDM


#print(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch(symptom_name))))

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

atc_codes = get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file,  get_umls_from_elasticsearch(symptom_name))))
#print(atc_codes)



"""
STEP 4 : Find drug name from atc code List
"""

def concatSource(a,b):
    return a + " "*10 + b

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

#print(get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch(symptom_name)))) ))
#print(len(get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch("headache")))) )))
#print(len(get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch("stomach ache")))) )))

"""
print("-"*50)
print("STITCH")
print("-"*50)
print(get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch("headache")))) ))
"""

###########################
# Seconde Method : DRUGBANK 
###########################


def search_toxicity(symptom):
    #symptom = recognize_symptom(symptom)
    #print(symptom)



    has_wildcard = ("*" in symptom or "?" in symptom)
    
    if has_wildcard:
      
        query = {
            "query": {
                "query_string": {
                    "query": symptom,              
                    "fields": ["toxicity", "synonyms"],  
                    "default_operator": "AND"
                }
            },
            "size": 100 
        }
    else : 
        query = {
            "query": {
                "match": {
                    "toxicity": {
                        "query": symptom,
                        "operator": "and" 
                    }
                }
            },
            "_source": ["name", "toxicity"],  
            "size": 1000 
        }

    response = es.search(index="drugbank", body=query)
        
    medications = []
        
    for hit in response['hits']['hits']:
        medication = hit['_source']
        medications.append(medication['name'])
    
    return medications


from sort import *
def build_cid_to_drugs_map(cids_list, file_path):
    """
    Construit un dict { cid: [drug_name1, drug_name2,...] } 
    en utilisant la logique convert_CIDM -> get_atc_by_cidm -> get_drug_by_atc.
    """
    if not cids_list: 
        return {}

    cid_to_drugs = {}
    for cid in cids_list:
        numeric_part = int(cid[3:]) - 100000000
        cidm = f"CIDm{numeric_part:08d}"

        atcs = get_atc_by_cidm([cidm])
        drug_names = get_drug_by_atc(file_path, atcs)

        cid_to_drugs[cid] = drug_names

    return cid_to_drugs


def search_toxicity_final(symptom):
    meddra_se_file = 'data/SIDER/meddra_all_se.tsv'
    meddra_freq_file = 'data/SIDER/meddra_freq.tsv'

    # Find CIDs + UMLS code 
    umls_list = get_umls_from_elasticsearch(symptom)
    cids_list = get_cid_from_umls(meddra_se_file, umls_list)
    if not cids_list:
        return {}


    # Frequence for each CID 
    # Filter by uml_code 
    cid_to_score = {}
    if cids_list:
        cid_to_score = get_cid_frequencies(meddra_freq_file, cids_list, umls_list)

    # mapping cid -> [drug_names]
    cid_to_drugs = build_cid_to_drugs_map(cids_list, file_path)

    # Score 
    element_source = {}
    

    for cid in cids_list:
        freq_value = cid_to_score.get(cid, None)

        meds_for_this_cid = cid_to_drugs.get(cid, [])

        for med in meds_for_this_cid:
            if med not in element_source:
                element_source[med] = {
                    "source": "STITCH",
                    "score": freq_value
                }
            else:
                # drug already exists -> max 
                current_score = element_source[med]["score"]
                if current_score is None:
                    element_source[med]["score"] = freq_value
                else:
                    # take max 
                    if freq_value is not None:
                        element_source[med]["score"] = max(current_score, freq_value)

    # DRUGBANK
    List_DRUGBANK = search_toxicity(symptom)
    for drug_name in List_DRUGBANK:
        if drug_name in element_source:
            element_source[drug_name]["source"] = "STITCH + DRUGBANK"
        else:
            element_source[drug_name] = {
                "source": "DRUGBANK",
                "score": None
            }

    return element_source


"""

print("*"*10)
print(search_toxicity_final("headache"))


"""

####STATS DRUGBANK / STITCH / STICTH + DRUGBANK : 

def count_sources_SE(dico_drugs):
    drugbank = 0
    stitch = 0
    both = 0  # STITCH + DRUGBANK
    for drug, info in dico_drugs.items():
        source = info["source"] 
        if source == "STITCH":
            stitch += 1
        elif source == "DRUGBANK":
            drugbank += 1
        elif source == "DRUGBANK + STITCH" or source == "STITCH + DRUGBANK":
            both += 1
    return [stitch, drugbank, both]



def sort_dico_drugs(dico_drugs):
    """
    1) Trie selon l'ordre de priorité du "source"
    2) S'il y a égalité, on peut trier par score si tu le souhaites
    """
    priority_order = {
        "STITCH + DRUGBANK": 1,
        "DRUGBANK + STITCH": 1,
        "STITCH": 2,
        "DRUGBANK": 3
    }

    def priority(item):
        # item = (drug_name, {"source":..., "score":...})
        src = item[1]["source"]
        score = item[1].get("score", None)  
        
        if score is None:
            score = -1
        return (priority_order.get(src, 4), -score)

    # Sort priority by score then sources
    sorted_items = sorted(dico_drugs.items(), key=priority)
    return dict(sorted_items)
