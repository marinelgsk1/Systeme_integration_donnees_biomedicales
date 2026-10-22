from elasticsearch import Elasticsearch

def create_chemical_index(index_name="chemical_index"):
    """
    Creates an Elasticsearch index with a mapping for your chemical data.
    """
    es = Elasticsearch("http://localhost:9200")

    # Vérifier si l'index existe déjà
    if es.indices.exists(index=index_name):
        print(f"L'index '{index_name}' existe déjà. Vous pouvez le supprimer avant de le recréer.")
        return

    # Définir un mapping personnalisé
    mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "cidm": {"type": "keyword"},  # correspondance exacte pour CIDm
                "atc": {"type": "keyword"}    # correspondance exacte pour ATC
            }
        }
    }

    # Créer l'index avec le mapping
    es.indices.create(index=index_name, body=mapping)
    print(f"Index '{index_name}' créé avec succès.")


