from DIsease_SE import *
from get_umls import *
from find_treatment_drugs import *

####################################
#############Side effects########### 
####################################


def search_toxicity_List_AND(list_symptoms):

    if not list_symptoms:
        return {}

    dicts_for_each_symptom = [search_toxicity_final(s) for s in list_symptoms]

    common_drugs = set(dicts_for_each_symptom[0].keys())
    for d in dicts_for_each_symptom[1:]:
        common_drugs.intersection_update(d.keys())

    final_dict = {}
    for drug in common_drugs:
        combined_sources = set()
        scores = []
        for d in dicts_for_each_symptom:
            if drug in d:
                source_str = d[drug]["source"] 
                splitted = source_str.split(" + ") if " + " in source_str else [source_str]
                combined_sources.update(splitted)

                if d[drug]["score"] is not None:
                    scores.append(d[drug]["score"])

        final_source = " + ".join(sorted(combined_sources))
        final_score = max(scores) if scores else None

        final_dict[drug] = {
            "source": final_source,
            "score": final_score
        }

    return final_dict


def search_toxicity_List_OR(list_symptoms):
  
    if not list_symptoms:
        return {}

    dicts_for_each_symptom = [search_toxicity_final(s) for s in list_symptoms]

    all_drugs = set()
    for d in dicts_for_each_symptom:
        all_drugs.update(d.keys())
    final_dict = {}
    for drug in all_drugs:
        combined_sources = set()
        scores = []
        for d in dicts_for_each_symptom:
            if drug in d:
                source_str = d[drug]["source"]
                splitted = source_str.split(" + ") if " + " in source_str else [source_str]
                combined_sources.update(splitted)

                if d[drug]["score"] is not None:
                    scores.append(d[drug]["score"])

        final_source = " + ".join(sorted(combined_sources))
        final_score = max(scores) if scores else None

        final_dict[drug] = {
            "source": final_source,
            "score": final_score
        }

    return final_dict


"""
L = ["nausea", "headache"]
print("*"*10)
print(search_toxicity_List_OR(L))
"""


#print(len(get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch("headache")))) )))
#print(len(get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch("nausea")))) )))
#print(len(get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch("cramps")))) )))


####################################
########### Treatment###############
####################################



def search_drugs_List_AND(List_symptom):
    if not List_symptom:
        return {}
    
    symptom_drug_sources = []
    
    for symptom in List_symptom:
        symptom_drug_sources.append(search_treatment_final(symptom))
    
    common_drugs = set.intersection(*map(set, symptom_drug_sources))
    
    final_sources = {}
    for drug in common_drugs:
        sources = set()
        for drug_sources in symptom_drug_sources:
            if drug in drug_sources:
                sources.update(drug_sources[drug].split(" + "))
        final_sources[drug] = " + ".join(sorted(sources))
    
    return final_sources



def search_drugs_List_OR(List_symptom):
    if not List_symptom:
        return {}
    
    all_drug_sources = {}
    
    for symptom in List_symptom:
        symptom_drug_sources = search_treatment_final(symptom)
        for drug, source in symptom_drug_sources.items():
            if drug in all_drug_sources:
                existing_sources = set(all_drug_sources[drug].split(" + "))
                new_sources = set(source.split(" + "))
                all_drug_sources[drug] = " + ".join(sorted(existing_sources.union(new_sources)))
            else:
                all_drug_sources[drug] = source
    
    return all_drug_sources

"""
L = [ "headache", "fever"]
print(len(search_drugs_List_AND(L)))
print(len(search_drugs_List_OR(L)))

print(len(search_treatment_final("headache")))
print(len(search_treatment_final("nausea")))
print(len(search_treatment_final("fever")))
"""

####################################
########### Diseases ###############
####################################



from disease import *
from search_symptom import *


def search_diseases_List_AND(symptoms_list):
    

    # For each symptom => 'search_hpo' => 'get_diseases_for_hpo' 
    # store diesases in set 

    all_sets = []
    for symptom in symptoms_list:
        hpo_matches = search_hpo(symptom)
        diseases_for_this_symptom = set()
        for match in hpo_matches:
            hpo_id = match["id"]
            these_diseases = get_diseases_for_hpo(hpo_id, db_path="data/HPO/hpo_annotations.sqlite")
            diseases_for_this_symptom.update(these_diseases)

        all_sets.append(diseases_for_this_symptom)

    if not all_sets:
        return []
    
    final_diseases = set.intersection(*all_sets)
    return list(final_diseases)

def search_diseases_List_OR(symptoms_list):
  
    result_set = set()
    for symptom in symptoms_list:
        hpo_matches = search_hpo(symptom)
        for match in hpo_matches:
            hpo_id = match["id"]
            these_diseases = get_diseases_for_hpo(hpo_id, db_path="data/HPO/hpo_annotations.sqlite")
            result_set.update(these_diseases)

    return list(result_set)


###DICT : 


def search_diseases_List_AND2(symptoms_list):
  
    all_sets = []
    
    for symptom in symptoms_list:
        hpo_matches = search_hpo(symptom)
        diseases_for_this_symptom = {}

        for match in hpo_matches:
            hpo_id = match["id"]
            disease_dict = dico_disease(hpo_id, db_path="data/HPO/hpo_annotations.sqlite")
            diseases_for_this_symptom.update(disease_dict)  

        if diseases_for_this_symptom: 
            all_sets.append(set(diseases_for_this_symptom.items())) 
    
    if not all_sets:
        return {}

    final_diseases = set.intersection(*all_sets)

    return dict(final_diseases)


def search_diseases_List_OR2(symptoms_list):
  
    result_dict = {}

    for symptom in symptoms_list:
        hpo_matches = search_hpo(symptom)

        for match in hpo_matches:
            hpo_id = match["id"]
            disease_dict = dico_disease(hpo_id, db_path="data/HPO/hpo_annotations.sqlite")
            result_dict.update(disease_dict)  

    return result_dict


#print(len(search_diseases_List_AND2(["headache", "fever"])))
#print(len(search_diseases_List_OR2(["headache", "fever"])))


def count_sources_diseases(dico_diseases):
    omim = 0
    orpha = 0 
    L=[]
    for key in dico_diseases:
        if dico_diseases[key]=="OMIM":
            omim+=1
        elif dico_diseases[key]=="ORPHA":
            orpha+=1
       
    L.append(omim)
    L.append(orpha)
    return L 