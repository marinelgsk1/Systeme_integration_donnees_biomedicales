import json

def tsv_to_json(tsv_file, json_file):
    """
    Convert the TSV file to JSON format, keeping only CIDm and ATC fields.
    Each line will become one JSON object: {"cidm": ..., "atc": ...}
    """
    data = []
    with open(tsv_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments or empty lines
            if not line or line.startswith("#"):
                continue
            
            parts = line.split("\t")
            # We expect something like:
            # CIDm00028871    CIDs00028871    ATC     M01AB10
            if len(parts) < 4:
                continue
            
            cidm = parts[0]  # ex: CIDm00028871
            source_type = parts[2]  # ex: ATC
            atc_code = parts[3]     # ex: M01AB10

            # On ne garde que les lignes ATC
            if source_type == "ATC":
                data.append({
                    "cidm": cidm,
                    "atc": atc_code
                })
    
    # Écriture du JSON
    with open(json_file, "w", encoding="utf-8") as jf:
        json.dump(data, jf, indent=2, ensure_ascii=False)
    
    print(f"{len(data)} lignes converties et enregistrées dans {json_file}")

# Exemple d'utilisation
tsv_file = "../chemical.sources.v5.0.tsv/chemical.sources.v5.0.tsv"
json_file = "chemical_data.json"
tsv_to_json(tsv_file, json_file)
