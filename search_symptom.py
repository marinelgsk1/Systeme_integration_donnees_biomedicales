from elasticsearch import Elasticsearch

INDEX_NAME = "hpo_index"

def search_hpo(symptom):
    """
    Cherche des documents dans Elasticsearch où 'symptom' apparaît
    comme sous-chaîne dans name.keyword ou synonyms.keyword
    si l'utilisateur met ou non un wildcard. Sinon, on fait un match text.
    """

    es = Elasticsearch("http://localhost:9200")

    has_wildcard = ("*" in symptom or "?" in symptom)

    if has_wildcard:
          # If the user explicitly included a wildcard, we respect it.
        # BUT we can make it more user-friendly by adding * at the beginning/end
        # to allow matches anywhere inside the .keyword field.
        
        # Example: if the user types "heada*", we transform it into "*heada*"
        # to capture any case where 'heada' is a substring.
        pattern = symptom
       
        if not pattern.endswith("*"):
            pattern = pattern + "*"

        query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "wildcard": {
                                "name.keyword": {
                                    "value": pattern,
                                    "case_insensitive": True,
                                }
                            }
                        },
                        {
                            "wildcard": {
                                "synonyms.keyword": {
                                    "value": pattern,
                                    "case_insensitive": True
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            "size": 1000
        }
    else:
               # If the user explicitly included a wildcard, we respect it.
        # BUT we can make it more user-friendly by adding * at the beginning/end
        # to allow matches anywhere inside the .keyword field.
        
        # Example: if the user types "heada*", we transform it into "*heada*"
        # to capture any case where 'heada' is a substring.

        query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match_phrase": {
                                "name": symptom
                            }
                        },
                        {
                            "match_phrase": {
                                "synonyms": symptom
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            "size": 1000
        }


    response = es.search(index=INDEX_NAME, body=query)
    hits = response["hits"]["hits"]
    if not hits:
        return []

    hpo_results = []
    for hit in hits:
        source = hit["_source"]
        hpo_results.append({
            "id": source.get("id"),
            "name": source.get("name"),
            "synonyms": source.get("synonyms", [])
        })
       

    return hpo_results

