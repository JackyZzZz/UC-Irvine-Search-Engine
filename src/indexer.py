import os
import json
import logging
from collections import defaultdict
from tokenizer import Tokenizer
from utils import setup_logging, save_json
from config import DATA_DIR, PARTIAL_INDEX_DIR, DOC_MAPPING_FILE, LOG_FILE, BATCH_SIZE

def build_partial_indexes():
    setup_logging(LOG_FILE)
    tokenizer = Tokenizer()
    inverted_index = defaultdict(list)
    doc_mapping = {}
    doc_id = 1
    partial_count = 1
    total_docs = 0

    print("Starting indexing process...")
    try:
        for domain in os.listdir(DATA_DIR):
            domain_path = os.path.join(DATA_DIR, domain)
            if os.path.isdir(domain_path):
                print(f"\nProcessing domain: {domain}")
                domain_docs = 0
                
                for file in os.listdir(domain_path):
                    file_path = os.path.join(domain_path, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            data = json.load(f)
                            url = data.get('url', '')
                            content = data.get('content', '')
                            doc_mapping[doc_id] = url
                            tokens = tokenizer.tokenize_and_stem(content)
                            
                            # Process document
                            term_freq = defaultdict(int)
                            for token in tokens:
                                term_freq[token] += 1
                            for token, freq in term_freq.items():
                                inverted_index[token].append([doc_id, freq])
                            
                            doc_id += 1
                            domain_docs += 1
                            total_docs += 1

                            if total_docs % 100 == 0:  # Progress update every 100 documents
                                print(f"Processed {total_docs} documents...")

                        if (doc_id - 1) % BATCH_SIZE == 0:
                            print(f"\nSaving partial index {partial_count} ({len(inverted_index)} terms)...")
                            partial_path = os.path.join(PARTIAL_INDEX_DIR, f'partial_{partial_count}.json')
                            save_json(inverted_index, partial_path)
                            print(f"Saved {partial_path}")
                            inverted_index = defaultdict(list)
                            partial_count += 1

                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                        logging.error(f"Error processing file {file_path}: {e}")
                
                print(f"Completed domain {domain}: processed {domain_docs} documents")

        # Save any remaining documents
        if inverted_index:
            print(f"\nSaving final partial index {partial_count}...")
            partial_path = os.path.join(PARTIAL_INDEX_DIR, f'partial_{partial_count}.json')
            save_json(inverted_index, partial_path)
            print(f"Saved {partial_path}")

        # Save document mapping
        print("\nSaving document mapping...")
        save_json(doc_mapping, DOC_MAPPING_FILE)
        print(f"Indexing complete! Processed {total_docs} documents in total")

    except Exception as e:
        print(f"Critical error: {e}")
        logging.critical(f"Critical error: {e}")

if __name__ == "__main__":
    build_partial_indexes()
