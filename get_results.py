

from flask import Flask, request, render_template
from search_symptom import search_hpo
from disease import get_diseases_for_hpo
from DIsease_SE import *
from get_umls import get_umls_from_elasticsearch
import json
from OR_AND_disease import *
from find_treatment_drugs import *
from omim_parser import *

def get_results(symptoms, operator): 
    """

    Main function to retrieve the data

    
    """
    hpo_matches = []

    if symptoms and (operator == "AND" or operator == "OR"):
    # If user selected OR logic
        if operator == "OR":
            dico_drugs = sort_dico_drugs(search_toxicity_List_OR(symptoms))
            sources_stat_drugs = count_sources_SE(dico_drugs)

            dico_treamtent = sort_dico_drugs2(search_drugs_List_OR(symptoms))
            sources_stat_treatment = count_sources_SE2(dico_treamtent)

            #all_diseases = search_diseases_List_OR(symptoms)
            dico_diseases = search_diseases_List_OR2(symptoms)
            sources_stat_diseases = count_sources_diseases(dico_diseases)

            for symptom in symptoms:
                hpo_matches.extend(search_hpo(symptom))



 # If user selected AND logic
        elif operator == "AND":
            dico_drugs = sort_dico_drugs(search_toxicity_List_AND(symptoms))
            sources_stat_drugs = count_sources_SE(dico_drugs)
        

         
            dico_treamtent = sort_dico_drugs2(search_drugs_List_AND(symptoms))
            sources_stat_treatment = count_sources_SE2(dico_treamtent)

            dico_diseases = search_diseases_List_AND2(symptoms)
            #all_diseases = search_diseases_List_AND(symptoms)
            sources_stat_diseases = count_sources_diseases(dico_diseases)

            for symptom in symptoms:
                hpo_matches.extend(search_hpo(symptom))


         
    else:
 # If only one symptom provided
        symptom = symptoms[0] if len(symptoms) == 1 else None

        dico_drugs =  sort_dico_drugs(search_toxicity_final(symptom))
        sources_stat_drugs = count_sources_SE(dico_drugs)

        #meds=get_drug_by_atc(file_path, get_atc_by_cidm(convert_CIDM(get_cid_from_umls(tsv_file, get_umls_from_elasticsearch(symptom)))) )
        
        dico_treamtent = sort_dico_drugs2(search_treatment_final(symptom))
        sources_stat_treatment = count_sources_SE2(dico_treamtent)




       # Retrieve HPO matches

        hpo_matches = search_hpo(symptom)
    
        dico_diseases={}
        for match in hpo_matches:
            hpo_id = match["id"]
            disease_dict1 = dico_disease(hpo_id, db_path="data/HPO/hpo_annotations.sqlite")
            dico_diseases.update(disease_dict1)  
        # ➕ Additionally fetch OMIM diseases if only one symptom was given
        omim_diseases = search_symptom(symptom)
        for disease in omim_diseases:
            if disease not in dico_diseases:
                dico_diseases[disease] = "OMIM"


        sources_stat_diseases = count_sources_diseases(dico_diseases)

    return dico_drugs, dico_treamtent, dico_diseases, \
        sources_stat_drugs, sources_stat_treatment, sources_stat_diseases, hpo_matches \
            
    
