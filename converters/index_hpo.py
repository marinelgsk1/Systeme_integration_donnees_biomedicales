from elasticsearch import Elasticsearch, helpers
import json

es = Elasticsearch("http://localhost:9200")


INDEX_NAME = "hpo_index"  


def index_hpo_data(json_file):
    """
    Creates (or recreates) the index with a custom mapping + normalizer,
    then indexes HPO data from the specified JSON file into Elasticsearch.
    """


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
                "id": {
                    "type": "keyword"
                },
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "normalizer": "my_lowercase_normalizer"
                        }
                    }
                },
                "synonyms": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "normalizer": "my_lowercase_normalizer"
                        }
                    }
                }
            }
        }
    }


    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)


    es.indices.create(index=INDEX_NAME, body=body)

    with open(json_file, "r", encoding="utf-8") as f:
        hpo_data = json.load(f) 

    actions = [
        {
            "_index": INDEX_NAME,
            "_id": entry["id"], 
            "_source": entry
        }
        for entry in hpo_data
    ]


    helpers.bulk(es, actions)
    print(f"Indexed {len(hpo_data)} documents into Elasticsearch with the new mapping.")


if __name__ == "__main__":
    index_hpo_data("hpo_data.json")
 
