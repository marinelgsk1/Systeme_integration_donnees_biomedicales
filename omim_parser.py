import json
from elasticsearch import Elasticsearch, helpers
import re


es = Elasticsearch("http://localhost:9200")


def parse_omim_file(filepath):
    """
     Parses an OMIM-like file:
    - Each record starts with '*RECORD*'
    - Each field is introduced by '*FIELD* <field_name>'
    Returns a list of dictionaries, each representing a record.
    Possible keys include: 'no', 'ti', 'tx', 'cs', etc., plus:
    'record_no' : Normalized identifier (uses 'no' if available)
    'all_text'  : Concatenated content for full-text search
    """

    records = [] # to store each disease
    current_record = {} # a dict for each disease
    current_field_name = None
    current_field_content = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n') # remove \n

           
            if line.startswith('*RECORD*'):# new record
               
                if current_record:
                    if current_field_name:
                        current_record[current_field_name] = "\n".join(current_field_content).strip()

              
                    all_text = []
                    for k, v in current_record.items():
                        if k not in ['record_no', 'no']:
                            all_text.append(v)
                    current_record['all_text'] = "\n".join(all_text)

                    records.append(current_record)

     
                current_record = {}
                current_field_name = None
                current_field_content = []
                continue

   
            elif line.startswith('*FIELD* '):
  
                if current_field_name:
                    current_record[current_field_name] = "\n".join(current_field_content).strip()

                parts = line.split(' ', 1) # return a list with the parts separated by ' '
                #print( parts)
                if len(parts) == 2:
                    field_name = parts[1].strip().lower()#for the name of the field
                else:
                    field_name = "unknown"

                current_field_name = field_name
                current_field_content = []

            else:
               
                current_field_content.append(line)

       
        if current_record:
            if current_field_name:
                current_record[current_field_name] = "\n".join(current_field_content).strip()

            all_text = []
            for k, v in current_record.items():
                if k not in ['record_no', 'no']:
                    all_text.append(v)
            current_record['all_text'] = "\n".join(all_text)

            records.append(current_record)

    # Normalise 'record_no'
    for rec in records:
        if 'no' in rec:
            rec['record_no'] = rec['no']
        elif 'record_no' not in rec:
            rec['record_no'] = "Unknown"

    return records


def create_index(index_name="omim_index"):
    """
    Creates an index in Elasticsearch with an appropriate mapping.
    """
    mapping_body = {
        "mappings": {
            "properties": {
                "record_no": {"type": "keyword"},
                "title":     {"type": "text"},
                "tx":        {"type": "text"},
                "cs":        {"type": "text"},
                "all_text":  {"type": "text"}
            }
        }
    }


    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=mapping_body)
        print(f"Index '{index_name}' has been created.")
    else:
        print(f"Index '{index_name}' already exists.")


def index_data(records, index_name="omim_index"):
    """
    Performs a bulk insert of the 'records' list into the Elasticsearch index.
    """
    actions = []
    for rec in records:
        record_no = rec.get('record_no', "Unknown")
        title     = rec.get('ti', "")
        tx        = rec.get('tx', "")
        cs        = rec.get('cs', "")
        all_text  = rec.get('all_text', "")

        action = {
            "_index": index_name,
            "_id": record_no, 
            "_source": {
                "record_no": record_no,
                "title": title,
                "tx": tx,
                "cs": cs,
                "all_text": all_text
            }
        }
        actions.append(action)

    response = helpers.bulk(es, actions)
    print("Bulk indexing done. Response:", response)


def search_symptom(symptom, index_name="omim_index"):
    """
    Performs a full-text search for a symptom in the 'all_text' field.  
    Limits the results to 10 entries.
    """
    query_body = {
    "query": {
        "match": {
            "cs": symptom  
        }
    },
    "size":10
    
}


    response = es.search(index=index_name, body=query_body)
    hits = response["hits"]["hits"]
    disease_names = []
    for hit in hits:
        title = hit["_source"]["title"]

     
        clean_title = re.sub(r"^[#%]?\d+\s*", "", title).strip()
        
        disease_names.append(clean_title)

    #print(f"Nombre de maladies associées à '{symptom}': {len(disease_names)}")
   # print("\n".join(disease_names))  # Afficher les noms des maladies nettoyés

    return disease_names  

# ---------------- MAIN / DEMO ----------------
if __name__ == "__main__":
    # 1) Parser le fichier omim.txt
    omim_file = "data/OMIM/omim.txt"  # Chemin vers ton fichier OMIM
    omim_records = parse_omim_file(omim_file)
    print("=> Nombre de records parsés:", len(omim_records))

    # 2) Supprimer l'index s'il existe (optionnel, pour repartir de zéro)
    es.indices.delete(index="omim_index", ignore=[400, 404])

    # 3) Créer l'index
    create_index(index_name="omim_index")

    # 4) Indexer en bulk
    index_data(omim_records, index_name="omim_index")

    
