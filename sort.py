
import csv
def get_cid_frequencies(meddra_freq_file, cids_interesses, umls_list):
    """
    Returns a dictionary { CID : maximum frequency related to the symptom }  
    The symptom is identified by a UMLS code (column [2] or [4]).
    """
    frequencies = {}
    cids_set = set(cids_interesses)
    umls_set = set(umls_list)

    with open(meddra_freq_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) < 6:
                continue
            cid = row[0]
            umls_code_1 = row[2]
            umls_code_2 = row[4]

            
            if cid in cids_set and (umls_code_1 in umls_set or umls_code_2 in umls_set):
                try:
                    freq_value = float(row[6])
                except ValueError:
                    try:
                        freq_value = float(row[4].replace('%', '').strip()) / 100.0
                    except:
                        freq_value = 0.0

                if cid not in frequencies:
                    frequencies[cid] = freq_value
                else:
                    frequencies[cid] = max(frequencies[cid], freq_value)

    return frequencies
# meddra_freq_file = "data/SIDER/meddra_freq.tsv"

# test_cid = "CID100000085"
# test_umls = "C0018681"

# result = get_cid_frequencies(meddra_freq_file, [test_cid], [test_umls])

# print("Résultat du test :")
# print(result)
