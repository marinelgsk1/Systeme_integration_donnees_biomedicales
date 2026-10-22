from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")  

INDEX_NAME = "hpo_index"  # Index name

def get_umls_from_elasticsearch(symptom):
    """
    Searches for a symptom in Elasticsearch and returns the associated UMLS codes.
    If the user includes wildcards (* or ?), a query_string query is used to support wildcard searches.
    Otherwise, a multi_match query with fuzziness is used to allow slight spelling mistakes.
    """
    has_wildcard = ("*" in symptom or "?" in symptom)
    
    if has_wildcard:
        # If the user provides wildcards, use a query_string query
        query = {
            "query": {
                "query_string": {
                    "query": symptom,                # Example: "fev*" or "???itis"
                    "fields": ["name", "synonyms"],  # Fields to search in
                    "default_operator": "AND"
                }
            },
            "size": 100  # Limit the number of results
        }
    else:
        # If no wildcard, use a multi_match query with fuzziness to allow minor typos
        query = {
                "query": {
                    "multi_match": {
                        "query": symptom,
                        "fields": ["name", "synonyms"],
                        "type": "phrase"  # match_phrase
                        # "slop": 0 si tu veux autoriser 0 mot d'écart
                    }
                },
                "size": 100
            }
    # Execute the search query
    response = es.search(index=INDEX_NAME, body=query)
    hits = response["hits"]["hits"]

    # Extract UMLS codes from the search results
    umls_codes = []
    for hit in hits:
        source = hit["_source"]
        if "umls" in source:  # Check if the 'umls' field exists
            umls_codes.extend(source["umls"])  # Add UMLS codes to the list

    # Return a deduplicated list of UMLS codes
    #print(list(set(umls_codes)))
    return list(set(umls_codes))

