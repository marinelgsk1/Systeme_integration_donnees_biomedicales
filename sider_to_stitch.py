from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")


def search_atc_by_cidm(cidm, index_name="chemical_index"):
    """
    Searches for ATC codes in Elasticsearch using a CIDm identifier.
    
    :param cidm: The CIDm identifier to search for.
    :param index_name: The Elasticsearch index name where the data is stored.
    :return: A list of unique ATC codes associated with the given CIDm.
    """
    query = {
        "query": {
            "match": {  
                "cidm": cidm  
            }
        }
    }

    # Execute search query
    response = es.search(index=index_name, body=query, size=1000)

    # Extract unique ATC codes from results
    atc_codes = {hit["_source"]["atc"] for hit in response["hits"]["hits"]}

    return list(atc_codes)  # Convert set to list for unique values

cidm_code = "CIDm00028871"  
atc_results = search_atc_by_cidm(cidm_code)

#print(f"ATC codes for {cidm_code}: {atc_results}")
