import os
import json
import logging
from collections import defaultdict
from tokenizer import Tokenizer
from utils import setup_logging, save_json
from config import DATA_DIR, PARTIAL_INDEX_DIR, DOC_MAPPING_FILE, LOG_FILE, BATCH_SIZE, LINKS_FILE
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_outbound_links(content, base_url):
    """
    Extracts outbound links from HTML content.

    :param content: HTML content as a string.
    :param base_url: The base URL of the document for resolving relative URLs.
    :return: A list of absolute outbound URLs.
    """
    soup = BeautifulSoup(content, 'html.parser')
    outbound_links = []

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_link = urljoin(base_url, href)
        outbound_links.append(full_link)

    return outbound_links

def build_partial_indexes():
    setup_logging(LOG_FILE)
    tokenizer = Tokenizer()
    inverted_index = defaultdict(list)  # token -> list of [doc_id, freq, positions]
    doc_mapping = {}
    doc_id = 1
    partial_count = 1
    total_docs = 0

    # Temporary storage for links in the form doc_id -> list_of_urls
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

                                # Skip URLs with fragments
                                parsed_url = urlparse(url)
                                if parsed_url.fragment:
                                    continue

                                doc_mapping[doc_id] = url

                                # Tokenize with weights
                                weighted_tokens = tokenizer.tokenize_with_weights(content)

                                # weighted_tokens: token -> weighted_frequency
                                for token, wfreq in weighted_tokens.items():
                                    # Store freq (wfreq) and empty list for positions
                                    inverted_index[token].append([doc_id, wfreq, []])

                                # Extract outbound links
                                outbound_links = extract_outbound_links(content, url)
                                if outbound_links:
                                    links_temp[doc_id].extend(outbound_links)

                                doc_id += 1
                                domain_docs += 1
                                total_docs += 1

                                if total_docs % 100 == 0:
                                    print(f"Processed {total_docs} documents...")

                            # Save partial indexes if batch size reached
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

        # Save any remaining documents
        if inverted_index:
            inverted_index = dict(sorted(inverted_index.items()))
            print(f"\nSaving final partial index {partial_count}...")
            partial_path = os.path.join(PARTIAL_INDEX_DIR, f'partial_{partial_count}.json')
            save_json(inverted_index, partial_path)
            print(f"Saved {partial_path}")

        # Save document mapping
        save_json(doc_mapping, DOC_MAPPING_FILE)
        print(f"Indexing complete! Processed {total_docs} documents in total")

        # Resolve URLs in links_temp to doc_ids
        url_to_doc_id = {v: k for k, v in doc_mapping.items()}
        links_graph = {}
        for source_doc_id, url_list in links_temp.items():
            outbound_doc_ids = []
            for u in url_list:
                # Normalize and also skip if fragment is present in outbound links (optional)
                parsed_out = urlparse(u)
                if parsed_out.fragment:
                    # If you prefer, you can remove the fragment to treat it as the same page:
                    # no_fragment_url = urlunparse(parsed_out._replace(fragment=''))
                    # if no_fragment_url in url_to_doc_id:
                    #     outbound_doc_ids.append(url_to_doc_id[no_fragment_url])
                    # else:
                    #     continue
                    continue  # Just skip link with fragment
                if u in url_to_doc_id:
                    outbound_doc_ids.append(url_to_doc_id[u])
            links_graph[source_doc_id] = outbound_doc_ids

        print(f"\nSaving links graph to {LINKS_FILE}...")
        save_json(links_graph, LINKS_FILE)

    except Exception as e:
        print(f"Critical error: {e}")
        logging.critical(f"Critical error: {e}")

if __name__ == "__main__":
    build_partial_indexes()
