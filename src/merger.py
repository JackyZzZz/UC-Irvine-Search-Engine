import os
import json
import logging
import math
from collections import defaultdict
from utils import setup_logging, save_json
from config import PARTIAL_INDEX_DIR, FINAL_INDEX_DIR, LOG_FILE, DOC_MAPPING_FILE, IDF_FILE

def compute_idf(final_index_dir, final_index_files, total_docs, idf_file):
    """
    Compute IDF for each term and save to idf_file.
    term postings are now in format: [doc_id, freq, [positions]]
    DF = len(postings)
    IDF = log10(total_docs / DF)
    """
    idf = {}
    for file in final_index_files:
        with open(os.path.join(final_index_dir, file), 'r') as f:
            index_data = json.load(f)
            for term, postings in index_data.items():
                df = len(postings)
                if df > 0:
                    idf[term] = math.log10(total_docs / df)
                else:
                    idf[term] = 0.0
    save_json(idf, idf_file)
    return idf

def compute_tfidf(index_chunk, idf):
    """
    Convert freq to TF-IDF by:
    TF = 1 + log10(freq) if freq > 0 else 0
    TF-IDF = TF * IDF

    Current posting format: [doc_id, freq, [positions]]
    After computation: [doc_id, tfidf, [positions]]
    """
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
            # Update entry in place:
            entry[1] = tfidf  # Replace freq with tf-idf
            # positions remain the same at entry[2]
    return index_chunk

def merge_partial_indexes():
    setup_logging(LOG_FILE)
    print("Starting merge process...")

    # Load doc_mapping to get total_docs
    if not os.path.exists(DOC_MAPPING_FILE):
        raise FileNotFoundError("Document mapping file not found. Cannot compute TF-IDF.")
    with open(DOC_MAPPING_FILE, 'r') as f:
        doc_mapping = json.load(f)
    doc_mapping = {int(k): v for k, v in doc_mapping.items()}
    total_docs = len(doc_mapping)
    print(f"Total documents: {total_docs}")

    partial_files = sorted(os.listdir(PARTIAL_INDEX_DIR))
    total_files = len(partial_files)
    
    print(f"Found {total_files} partial index files to merge")

    # Create final index files for letters a-z and digits 0-9
    example_data = {}
    for letter in range(ord('a'), ord('z') + 1):
        filename = f"{FINAL_INDEX_DIR}/{chr(letter)}_tokens.json"
        with open(filename, 'w') as json_file:
            json.dump(example_data, json_file)
    print("26 JSON files created from a_tokens.json to z_tokens.json.")

    for letter in range(ord('0'), ord('9') + 1):
        filename = f"{FINAL_INDEX_DIR}/{chr(letter)}_tokens.json"
        with open(filename, 'w') as json_file:
            json.dump(example_data, json_file)
    print("10 JSON files created from 0_tokens.json to 9_tokens.json.")

    # For non-alphanumeric starting tokens
    other_file = os.path.join(FINAL_INDEX_DIR, 'other_tokens.json')
    with open(other_file, 'w') as of:
        json.dump(example_data, of)
    print("Created other_tokens.json for non-alphanumeric starting tokens.")

    # Merge partial indexes
    try:
        # Load all final indexes in memory for efficient merging
        # (Optional optimization: you can also merge incrementally as before.)
        
        # Prepare a dictionary to hold final data in memory
        final_data = defaultdict(list)  # token -> postings lists

        for i, p_file in enumerate(partial_files, 1):
            p_path = os.path.join(PARTIAL_INDEX_DIR, p_file)
            print(f"Processing file {i}/{total_files}: {p_file}")
            try:
                with open(p_path, 'r', encoding='utf-8') as pf:
                    partial_index = json.load(pf)
                    for token, postings in partial_index.items():
                        final_data[token].extend(postings)
                logging.info(f"Merged {p_file}")
                print(f"Successfully merged {p_file}")
            except Exception as e:
                logging.error(f"Error merging file {p_path}: {e}")
                print(f"Error processing {p_file}: {e}")
                continue

        print("All partial indexes merged in memory. Now distributing to final files...")

        # Distribute tokens to their respective final index files
        # According to first character (a-z, 0-9, others)
        final_index_files_map = {chr(c): f"{chr(c)}_tokens.json" for c in range(ord('a'), ord('z')+1)}
        for c in range(ord('0'), ord('9')+1):
            final_index_files_map[chr(c)] = f"{chr(c)}_tokens.json"

        final_indexes = {}
        # Load all final index files into memory
        # (They are currently empty)
        for key, fname in final_index_files_map.items():
            with open(os.path.join(FINAL_INDEX_DIR, fname), 'r') as ff:
                final_indexes[key] = json.load(ff)

        # Handle others
        with open(other_file, 'r') as of:
            others_index = json.load(of)

        # Distribute tokens
        for token, postings in final_data.items():
            first_char = token[0].lower()
            if first_char.isalnum():
                target_index = final_indexes[first_char]
            else:
                target_index = others_index

            if token in target_index:
                target_index[token].extend(postings)
            else:
                target_index[token] = postings

        # Save all final index files back to disk
        for key, fname in final_index_files_map.items():
            path = os.path.join(FINAL_INDEX_DIR, fname)
            # Sort tokens alphabetically for consistency
            sorted_index = dict(sorted(final_indexes[key].items()))
            save_json(sorted_index, path)
            print(f"Saved {path}")

        # Save others
        others_path = os.path.join(FINAL_INDEX_DIR, 'other_tokens.json')
        sorted_others = dict(sorted(others_index.items()))
        save_json(sorted_others, others_path)
        print(f"Saved {others_path}")

        # Compute IDF
        print("Computing IDF values...")
        all_final_index_files = [f for f in os.listdir(FINAL_INDEX_DIR) if f.endswith('_tokens.json') or f == 'other_tokens.json']
        idf = compute_idf(FINAL_INDEX_DIR, all_final_index_files, total_docs, IDF_FILE)
        print(f"IDF values computed and saved to {IDF_FILE}")

        # Compute TF-IDF for each final index file
        print("Computing TF-IDF scores for final index files...")
        for final_file in all_final_index_files:
            final_path = os.path.join(FINAL_INDEX_DIR, final_file)
            with open(final_path, 'r') as f_final:
                index_data = json.load(f_final)

            # Compute TF-IDF
            index_data = compute_tfidf(index_data, idf)

            # Save back
            # Sort again after computation
            index_data = dict(sorted(index_data.items()))
            with open(final_path, 'w') as f_final:
                json.dump(index_data, f_final)
            print(f"TF-IDF scores computed and updated in {final_file}")

        print("Merge and TF-IDF computation completed successfully!")

    except Exception as e:
        logging.critical(f"Critical error during merging: {e}")
        print(f"Critical error occurred: {e}")

if __name__ == "__main__":
    merge_partial_indexes()
