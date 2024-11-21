import os
import json
import logging
from collections import defaultdict
from utils import setup_logging, save_json
from config import PARTIAL_INDEX_DIR, FINAL_INDEX_DIR, LOG_FILE

def merge_partial_indexes():
    setup_logging(LOG_FILE)
    print("Starting merge process...")
    
    final_index = defaultdict(list)
    partial_files = sorted(os.listdir(PARTIAL_INDEX_DIR))
    total_files = len(partial_files)
    
    print(f"Found {total_files} partial index files to merge")
    
    try:
        for i, p_file in enumerate(partial_files, 1):
            p_path = os.path.join(PARTIAL_INDEX_DIR, p_file)
            print(f"Processing file {i}/{total_files}: {p_file}")
            
            try:
                with open(p_path, 'r', encoding='utf-8') as pf:
                    partial_index = json.load(pf)
                    for token, postings in partial_index.items():
                        final_index[token].extend(postings)
                logging.info(f"Merged {p_file}")
                print(f"Successfully merged {p_file}")
            except Exception as e:
                logging.error(f"Error merging file {p_path}: {e}")
                print(f"Error processing {p_file}: {e}")

        print("\nSorting final index entries...")
        # Sort the tokens
        final_index = dict(sorted(final_index.items()))
        # Sort postings for each token by Frequency
        for token in final_index:
            final_index[token].sort(key=lambda x: x[1], reverse=True)

        # Save final inverted index
        final_index_path = os.path.join(FINAL_INDEX_DIR, 'final_inverted_index.json')
        print(f"Saving final index to {final_index_path}")
        save_json(final_index, final_index_path)
        logging.info(f"Final inverted index saved to {final_index_path}")
        print("Merge process completed successfully!")

    except Exception as e:
        logging.critical(f"Critical error during merging: {e}")
        print(f"Critical error occurred: {e}")

if __name__ == "__main__":
    merge_partial_indexes()
