import xml.etree.ElementTree as ET
import json
from elasticsearch import Elasticsearch, helpers


def xml_to_json(file_path):
    """
    Parses the DrugBank XML file and returns a list of dictionaries
    with key information, including the primary DrugBank ID and name.
    """
    result = []
    ns = {"db": "http://www.drugbank.ca"}  # Namespace pour les balises XML
    tree = ET.parse(file_path)
    root = tree.getroot()

    for drug in root.findall("db:drug", ns):

        # drugbank_id 
        drugbank_id = None
        for dbid in drug.findall("db:drugbank-id", ns):
            if dbid.get("primary") == "true":
                drugbank_id = dbid.text
                break

        # name
        name_elem = drug.find("db:name", ns)
        name = name_elem.text if name_elem is not None else None

        # indication
        indication_elem = drug.find("db:indication", ns)
        indication = indication_elem.text if indication_elem is not None else None

        # toxicity
        toxicity_elem = drug.find("db:toxicity", ns)
        toxicity = toxicity_elem.text if toxicity_elem is not None else None

        # atc_codes
        atc_codes = [
            code.get("code")
            for code in drug.findall("db:atc-codes/db:atc-code", ns)
            if code.get("code") is not None
        ]

    
        data = {
            "drugbank_id": drugbank_id,
            "name": name,
            "indication": indication,
            "toxicity": toxicity,
            "atc_codes": atc_codes if atc_codes else []
        }

        if any(v for v in data.values()):
            result.append(data)

    return result

# Convert xml to json 
json_data = xml_to_json("data/DRUGBANK/drugbank.xml")

with open("data/DRUGBANK/drugbank2.json", "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

print(f"{len(json_data)} médicaments extraits de drugbank.xml")



es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "drugbank"

json_file = 'data/DRUGBANK/drugbank2.json'

def create_index():
    body = {
        "settings": {
            "analysis": {
                "normalizer": {
                    "my_lowercase_normalizer": {
                        "type": "custom",
                        "filter": ["lowercase"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "drugbank_id": {"type": "keyword"},
                "name": {"type": "text", "fields": {"keyword": {"type": "keyword", "normalizer": "my_lowercase_normalizer"}}},
                "indication": {"type": "text"},
                "toxicity": {"type": "text"}
            }
        }
    }

    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    es.indices.create(index=INDEX_NAME, body=body)

def index_drugs():
    with open(json_file, 'r', encoding='utf-8') as f:
        drugs = json.load(f)
    
    actions = [
        {
            "_index": INDEX_NAME,
            "_id": drug["drugbank_id"],  # Utiliser le drugbank_id comme identifiant
            "_source": drug
        }
        for drug in drugs
    ]
    success, failed = helpers.bulk(es, actions, raise_on_error=True)
    print(f"{success} médicaments indexés avec succès.")

create_index()

index_drugs()

print(f"Les médicaments ont été extraits et indexés depuis {json_file} dans Elasticsearch.")
