import os
import json
import logging
from collections import defaultdict
from utils import setup_logging, save_json
from config import PARTIAL_INDEX_DIR, FINAL_INDEX_DIR, LOG_FILE

def merge_partial_indexes():
    setup_logging(LOG_FILE)
    print("Starting merge process...")
    
    partial_files = sorted(os.listdir(PARTIAL_INDEX_DIR))
    total_files = len(partial_files)
    
    print(f"Found {total_files} partial index files to merge")


    #Create 26 final index files for adding
    example_data = {}
    for letter in range(ord('a'), ord('z') + 1):
        filename = f"{FINAL_INDEX_DIR}/{chr(letter)}_tokens.json"
        with open(filename, 'w') as json_file:
            json.dump(example_data, json_file)

    print("26 JSON files created from a_tokens.json to z_tokens.json.")

    # numerical token file
    for letter in range(ord('0'), ord('9') + 1):
        filename = f"{FINAL_INDEX_DIR}/{chr(letter)}_tokens.json"
        with open(filename, 'w') as json_file:
            json.dump(example_data, json_file)

    print("10 JSON files created from 0_tokens.json to 9_tokens.json.")
    
    try:
        for i, p_file in enumerate(partial_files, 1):
            p_path = os.path.join(PARTIAL_INDEX_DIR, p_file)
            print(f"Processing file {i}/{total_files}: {p_file}")

            current_letter = None

            try:
                with open(p_path, 'r', encoding='utf-8') as pf:
                    partial_index = json.load(pf)
                    for token, postings in partial_index.items():

                        if not current_letter:
                            current_letter = token.lower()[0]
                            with open(f"{FINAL_INDEX_DIR}/{current_letter}_tokens.json", 'r') as final_index_file:
                                final_index = json.load(final_index_file)
                            print(f"Merging into {FINAL_INDEX_DIR}/{current_letter}_tokens.json")
                            
                        if token.lower()[0] == current_letter:
                            if token in final_index:
                                final_index[token] += postings
                            else:
                                final_index[token] = postings
                        else:
                            # Finish the previous index files, prepare to write to the next letter
                            with open(f"{FINAL_INDEX_DIR}/{current_letter}_tokens.json", 'w') as final_index_file:
                                json.dump(final_index, final_index_file)
                            print(f"Finish merging into {FINAL_INDEX_DIR}/{current_letter}_tokens.json")

                            current_letter = token.lower()[0]
                            with open(f"{FINAL_INDEX_DIR}/{current_letter}_tokens.json", 'r') as final_index_file:
                                final_index = json.load(final_index_file)   
                            print(f"Merging into {FINAL_INDEX_DIR}/{current_letter}_tokens.json")
                            if token in final_index:
                                final_index[token] += postings
                            else:
                                final_index[token] = postings

                with open(f"{FINAL_INDEX_DIR}/{current_letter}_tokens.json", 'w') as final_index_file:
                    json.dump(final_index, final_index_file)
                    print(f"Finish merging into {FINAL_INDEX_DIR}/{current_letter}_tokens.json")

                logging.info(f"Merged {p_file}")
                print(f"Successfully merged {p_file}")
            except Exception as e:
                logging.error(f"Error merging file {p_path}: {e}")
                print(f"Error processing {p_file}: {e}")

        print("Merge process completed successfully!")

    except Exception as e:
        logging.critical(f"Critical error during merging: {e}")
        print(f"Critical error occurred: {e}")

if __name__ == "__main__":
    merge_partial_indexes()
