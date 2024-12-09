import os
import json
import logging
from collections import defaultdict
from tokenizer import Tokenizer
from utils import setup_logging, save_json
from config import DATA_DIR, PARTIAL_INDEX_DIR, DOC_MAPPING_FILE, LOG_FILE, BATCH_SIZE, LINKS_FILE
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from simhash import Simhash

def extract_outbound_links(content, base_url):
    soup = BeautifulSoup(content, 'html.parser')
    outbound_links = set()

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_link = urljoin(base_url, href)
        
        parsed_link = urlparse(full_link)
        if parsed_link.fragment:
            continue

        outbound_links.add(full_link)

    return list(outbound_links)

def build_partial_indexes():
    setup_logging(LOG_FILE)
    tokenizer = Tokenizer()
    inverted_index = defaultdict(list)  # token -> list of [doc_id, weight, [positions]]
    doc_mapping = dict()
    exsisting_url = set()
    doc_id = 1
    partial_count = 1
    total_docs = 0
    exsisting_hash_values = []
    duplicate_threshold = 1

    links_temp = defaultdict(list)

    print("Starting indexing process...")
    try:
        for entry in os.listdir(DATA_DIR):
            data_entry_path = os.path.join(DATA_DIR, entry)
            if not os.path.isdir(data_entry_path):
                continue
            for data_folder in os.listdir(data_entry_path):
                domain_path = os.path.join(data_entry_path, data_folder)
                if os.path.isdir(domain_path):
                    print(f"\nProcessing domain: {data_folder}")
                    domain_docs = 0
                    
                    for file in os.listdir(domain_path):
                        file_path = os.path.join(domain_path, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                data = json.load(f)
                                url = data.get('url', '')
                                content = data.get('content', '')
                                soup = BeautifulSoup(content, 'html.parser')
                                text_content = soup.get_text(separator=' ')
                                clean_content = ' '.join(text_content.split())

                                current_simhash = Simhash(clean_content)
                                hash_value = current_simhash.value

                                if hash_value in existing_hash_values:
                                    print("An exact duplicate detected, skipping this one...")
                                    continue

                                duplicate_detected = False
                                for h_val in existing_hash_list:
                                    stored_simhash = Simhash(value=h_val)
                                    if current_simhash.distance(stored_simhash) < duplicate_threshold:
                                        duplicate_detected = True
                                        break
                                if duplicate_detected:
                                    print("A near duplicate detected, skipping this one...")
                                    continue

                                # Skip URLs with fragments
                                parsed_url = urlparse(url)
                                if parsed_url.fragment:
                                    continue

                                # Checking for duplicates and near duplicate:
                                sim_soup = BeautifulSoup(content, 'html.parser') 
                                for tag in sim_soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'noscript']):
                                    tag.decompose()
                                text = ' '.join(sim_soup.stripped_strings)
                                text = text.lower()
                                hash_value = Simhash(text)
                                duplicate_detected = False
                                for hash in exsisting_hash_values:
                                    if hash_value.distance(hash) <= duplicate_threshold:
                                        duplicate_detected = True
                                        break
                                if duplicate_detected:
                                    print("An similar file detected, skipping this one...")
                                    continue
                                exsisting_hash_values.append(hash_value)
                                exsisting_url.add(url)
                                doc_mapping[doc_id] = url
                                weighted_tokens = tokenizer.tokenize_with_positions_and_weights(content)

                                # weighted_tokens: token -> (total_weight, [positions])
                                for token, (wfreq, positions) in weighted_tokens.items():
                                    inverted_index[token].append([doc_id, wfreq, positions])

                                outbound_links = extract_outbound_links(content, url)
                                if outbound_links:
                                    links_temp[doc_id].extend(outbound_links)
                                    links_temp[doc_id] = list(set(links_temp[doc_id]))

                                doc_id += 1
                                domain_docs += 1
                                total_docs += 1

                                if total_docs % 100 == 0:
                                    print(f"Processed {total_docs} documents...")


                            if (doc_id - 1) % BATCH_SIZE == 0:
                                inverted_index = dict(sorted(inverted_index.items()))
                                print(f"\nSaving partial index {partial_count} ({len(inverted_index)} terms)...")
                                partial_path = os.path.join(PARTIAL_INDEX_DIR, f'partial_{partial_count}.json')
                                save_json(inverted_index, partial_path)
                                print(f"Saved {partial_path}")
                                inverted_index = defaultdict(list)
                                partial_count += 1

                        except Exception as e:
                            print(f"Error processing file {file_path}: {e}")
                            logging.error(f"Error processing file {file_path}: {e}")
                    
                    print(f"Completed domain {data_folder}: processed {domain_docs} documents")

        if inverted_index:
            inverted_index = dict(sorted(inverted_index.items()))
            print(f"\nSaving final partial index {partial_count}...")
            partial_path = os.path.join(PARTIAL_INDEX_DIR, f'partial_{partial_count}.json')
            save_json(inverted_index, partial_path)
            print(f"Saved {partial_path}")

        # Save document mapping
        save_json(doc_mapping, DOC_MAPPING_FILE)
        print(f"Indexing complete! Processed {total_docs} documents in total")

        url_to_doc_id = {v: k for k, v in doc_mapping.items()}
        links_graph = {}
        for source_doc_id, url_list in links_temp.items():
            outbound_doc_ids = set()
            for u in url_list:
                parsed_out = urlparse(u)
                if parsed_out.fragment:
                    continue
                if u in url_to_doc_id:
                    outbound_doc_ids.add(url_to_doc_id[u])
            links_graph[source_doc_id] = list(outbound_doc_ids)

        print(f"\nSaving links graph to {LINKS_FILE}...")
        save_json(links_graph, LINKS_FILE)

    except Exception as e:
        print(f"Critical error: {e}")
        logging.critical(f"Critical error: {e}")


if __name__ == "__main__":
    build_partial_indexes()