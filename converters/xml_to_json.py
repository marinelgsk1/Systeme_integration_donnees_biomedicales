import xml.etree.ElementTree as ET
import json

xml_file = 'data/DRUGBANK/drugbank.xml'
json_file = 'data/DRUGBANK/drugbank.json'

ns = {'db': 'http://www.drugbank.ca'}

drugs = []
drug_ids_seen = set()

# Stream through the XML file to save memory
context = ET.iterparse(xml_file, events=('end',))

for event, elem in context:
    if elem.tag == '{http://www.drugbank.ca}drug':
        # Get the primary drugbank ID
        drugbank_ids = elem.findall('db:drugbank-id', ns)
        drugbank_id_elem = next((id_elem for id_elem in drugbank_ids if id_elem.attrib.get('primary') == 'true'), None)
        name_elem = elem.find('db:name', ns)
        indication_elem = elem.find('db:indication', ns)
        toxicity_elem = elem.find('db:toxicity', ns)

        if drugbank_id_elem is not None and name_elem is not None:
            drug_id = drugbank_id_elem.text.strip()
            if drug_id not in drug_ids_seen:
                indication_text = indication_elem.text.strip() if indication_elem is not None and indication_elem.text else ""
                toxicity_text = toxicity_elem.text.strip() if toxicity_elem is not None and toxicity_elem.text else ""

                # Keep only drugs with indication or toxicity info
                if indication_text or toxicity_text:
                    drug = {
                        'drugbank_id': drug_id,
                        'name': name_elem.text.strip(),
                        'indication': indication_text,
                        'toxicity': toxicity_text
                    }
                    drugs.append(drug)
                    drug_ids_seen.add(drug_id)

        elem.clear()

# Write the result to a JSON file
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(drugs, f, indent=2, ensure_ascii=False)

print(f"{len(drugs)} drugs saved to {json_file}")
