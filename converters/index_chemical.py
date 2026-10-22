import json
from elasticsearch import Elasticsearch, helpers

# Connexion to Elasticsearch
es = Elasticsearch("http://localhost:9200")

def index_chemical_data(json_file, index_name="chemical_index"):
    """
    Indexes chemical data from a JSON file into Elasticsearch.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        chemical_data = json.load(f)  

    actions = [
        {
            "_index": index_name,
            "_id": entry["cidm"],  # use 'cidm' as unique id 
            "_source": entry
        }
        for entry in chemical_data
    ]

    # Bulk indexing in Elasticsearch
    helpers.bulk(es, actions)
    print(f"Indexé {len(chemical_data)} documents dans Elasticsearch sous l'index '{index_name}'.")

    
if __name__=="__main__":
    index_chemical_data("chemical_data.json") 

