import os
import json
import logging
import math
from collections import defaultdict
from parse_file import processing_final_tokens
from utils import setup_logging, save_json, load_json
from config import (
    PARTIAL_INDEX_DIR, 
    FINAL_INDEX_DIR, 
    LOG_FILE, 
    DOC_MAPPING_FILE, 
    IDF_FILE, 
    DF_FILE  
)

def compute_idf(df_map, total_docs, idf_file):
    idf = {}
    for term, df in df_map.items():
        if df > 0:
            idf[term] = math.log10(total_docs / df)
        else:
            idf[term] = 0.0
    save_json(idf, idf_file)
    return idf

def compute_tfidf(index_chunk, idf):
    for token, postings in index_chunk.items():
        term_idf = idf.get(token, 0.0)
        for entry in postings:
            doc_id = entry[0]
            freq = entry[1]
            positions = entry[2]
            if freq > 0:
                tf = 1 + math.log10(freq)
            else:
                tf = 0
            tfidf = tf * term_idf
            entry[1] = tfidf  # Replace freq with tf-idf
    return index_chunk

def merge_partial_indexes():
    setup_logging(LOG_FILE)

    if not os.path.exists(DOC_MAPPING_FILE):
        raise FileNotFoundError("Document mapping file not found. Cannot compute TF-IDF.")
    with open(DOC_MAPPING_FILE, 'r') as f:
        doc_mapping = json.load(f)
    doc_mapping = {int(k): v for k, v in doc_mapping.items()}
    total_docs = len(doc_mapping)
    print(f"Total documents: {total_docs}")

    partial_files = sorted(os.listdir(PARTIAL_INDEX_DIR))
    total_files = len(partial_files)
    

    example_data = {}
    for letter in range(ord('a'), ord('z') + 1):
        filename = os.path.join(FINAL_INDEX_DIR, f"{chr(letter)}_tokens.json")
        with open(filename, 'w') as json_file:
            json.dump(example_data, json_file)
    print("26 JSON files created from a_tokens.json to z_tokens.json.")

    for digit in range(ord('0'), ord('9') + 1):
        filename = os.path.join(FINAL_INDEX_DIR, f"{chr(digit)}_tokens.json")
        with open(filename, 'w') as json_file:
            json.dump(example_data, json_file)
    print("10 JSON files created from 0_tokens.json to 9_tokens.json.")

    df_map = defaultdict(int)
    if os.path.exists(DF_FILE):
        with open(DF_FILE, 'r') as df_file:
            existing_df = json.load(df_file)
            for term, df in existing_df.items():
                df_map[term] += df

    # Merge partial indexes incrementally
    try:
        for i, p_file in enumerate(partial_files, 1):
            p_path = os.path.join(PARTIAL_INDEX_DIR, p_file)
            try:
                with open(p_path, 'r', encoding='utf-8') as pf:
                    partial_index = json.load(pf)
            except Exception as e:
                print(f"Error loading {p_file}: {e}")
                continue

            tokens_by_letter = defaultdict(list)
            for token, postings in partial_index.items():
                first_char = token[0].lower()
                tokens_by_letter[first_char].append((token, postings))
                df_map[token] += len(postings)


            for letter, tokens in tokens_by_letter.items():
                final_index_file = os.path.join(FINAL_INDEX_DIR, f"{letter}_tokens.json")
                try:
                    with open(final_index_file, 'r') as ff:
                        final_index = json.load(ff)
                except Exception as e:
                    print(f"Error loading final index file {final_index_file}: {e}")
                    continue

                for token, postings in tokens:
                    if token in final_index:
                        final_index[token].extend(postings)
                    else:
                        final_index[token] = postings

                sorted_final_index = dict(sorted(final_index.items()))
                save_json(sorted_final_index, final_index_file)


            print(f"Successfully merged {p_file}")


        save_json(df_map, DF_FILE)
        print(f"DF values saved to {DF_FILE}")

        idf = compute_idf(df_map, total_docs, IDF_FILE)
        print(f"IDF values computed and saved to {IDF_FILE}")

        # Compute TF-IDF for each final index file
        for final_file in [f for f in os.listdir(FINAL_INDEX_DIR) if f.endswith('_tokens.json')]:
            final_path = os.path.join(FINAL_INDEX_DIR, final_file)
            try:
                with open(final_path, 'r') as f_final:
                    index_data = json.load(f_final)

                index_data = compute_tfidf(index_data, idf)

                sorted_index_data = dict(sorted(index_data.items()))
                save_json(sorted_index_data, final_path)
                print(f"TF-IDF scores computed and updated in {final_file}")
            except Exception as e:
                print(f"Error processing final index file {final_path}: {e}")
                continue

        print("Merge and TF-IDF computation completed successfully!")

        # Convert the file and data structures of the final index files for quicker retrieval
        print("Staring converting indexes from json to txt")
        processing_final_tokens()

    except Exception as e:
        print(f"Critical error occurred: {e}")

if __name__ == "__main__":
    merge_partial_indexes()
