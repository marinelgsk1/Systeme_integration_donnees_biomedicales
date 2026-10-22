import re
import json

def parse_hpo_obo_to_json(obo_file, output_json):
    """
    Parses the HPO .obo file and converts it to JSON format for Elasticsearch.
    
    - Each HPO term is stored as a JSON document.
    - Extracts HPO ID, name, synonyms, and definition.
    """
    hpo_data = []
    current_id = None
    current_name = None
    current_syns = []
    current_def = ""
    current_umls=[]

    with open(obo_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Start of a new term
            if line == "[Term]":
                if current_id:  
                    hpo_data.append({
                        "id": current_id,
                        "name": current_name,
                        "synonyms": current_syns,
                        "definition": current_def,
                        "umls": current_umls
                        
                    })

                # Reset for next term
                current_id = None
                current_name = None
                current_syns = []
                current_def = ""
                current_umls=[]

            elif line.startswith("id: HP:"):
                current_id = line.split("id: ")[1].strip() #it splits at id: into 
                #two parts the '' befor di and HP after

            elif line.startswith("name: "):
                current_name = line.split("name: ")[1].strip()

            elif line.startswith("synonym: "):
                match = re.search(r'synonym:\s*"(.*?)"', line) # use regex
                if match:
                    current_syns.append(match.group(1))# match only the text between quotes

            elif line.startswith("def: "):
                match = re.search(r'def:\s*"(.*?)"', line)
                if match:
                    current_def = match.group(1)
            elif line.startswith("xref: UMLS:"):
                umls_code = line.split("xref: UMLS:")[1].strip()
                current_umls.append(umls_code)

    # Save the last term
    if current_id:
        hpo_data.append({
            "id": current_id,
            "name": current_name,
            "synonyms": current_syns,
            "definition": current_def,
            "umls":current_umls
        })

    # Write to JSON file
    with open(output_json, "w", encoding="utf-8") as json_file:
        json.dump(hpo_data, json_file, indent=2, ensure_ascii=False)

    print(f"Saved {len(hpo_data)} HPO terms to {output_json}")

# Run function
parse_hpo_obo_to_json("data/HPO/hpo.obo", "data/hpo_data.json")
