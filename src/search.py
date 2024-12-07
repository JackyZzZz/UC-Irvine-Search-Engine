import json
import argparse
from nltk.stem import PorterStemmer
from config import FINAL_INDEX_DIR, DOC_MAPPING_FILE
from math import log


def search_with_query(limit, *args):
    stemer = PorterStemmer()
    results = []

    # Load the inverted_index and doc mapping
    # with open(f"{FINAL_INDEX_DIR}/final_inverted_index.json") as file:
    #     data = json.load(file)
    with open(DOC_MAPPING_FILE) as file:
        map = json.load(file)

    total_num_docs = len(map)
    term_document_num_map = {}

    # Stem the query terms
    stemmed_terms = [stemer.stem(term) for term in args]

    docs_term_frequency_map = {}
    
    # Get document sets for each term
    term_docs = []
    for term in stemmed_terms:
        starting_letter = term.lower()[0]
        with open(f"{FINAL_INDEX_DIR}/{starting_letter}_tokens.json") as file:
            data = json.load(file)
        if term in data:
            for posting in data[term]:
                if posting[0] in docs_term_frequency_map:
                    docs_term_frequency_map[posting[0]].append((term, posting[1]))
                else:
                    docs_term_frequency_map[posting[0]] = [(term, posting[1])]
            docs = set(posting[0] for posting in data[term])
            term_document_num_map[term] = len(docs)
            term_docs.append(docs)
        else:
            return []

    # Intersect all document sets
    if term_docs:
        result_set = term_docs[0]
        for docs in term_docs[1:]:
            result_set = result_set.intersection(docs)

        # Calculate tf-df scores
        doc_scores = {}
        for doc_id in result_set:
            score = 0
            for token, frequency in docs_term_frequency_map[doc_id]:
                score += (1 + log(frequency)) * (1 + log(total_num_docs/term_document_num_map[token]))
            doc_scores[doc_id] = score

        # Calculate scores and deduplicate by base URL
        # url_scores = {}  # Dict to store highest score for each base URL
        # for doc_id in result_set:
        #     url = map[str(doc_id)]
        #     # Remove fragment from URL (everything after #)
        #     base_url = url.split('#')[0]
            
        #     # Calculate total frequency for this document
        #     total_freq = sum(posting[1] for term in stemmed_terms 
        #                    for posting in data[term] 
        #                    if posting[0] == doc_id)
            
        #     # Keep only highest scoring version of each URL
        #     if base_url not in url_scores or total_freq > url_scores[base_url][1]:
        #         url_scores[base_url] = (doc_id, total_freq)

        # Sort by frequency and output top k unique results
        sorted_results = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        for doc_id, _ in sorted_results:
            print(map[str(doc_id)])
            url = map[str(doc_id)]
            results.append({
                'url': url,
                'title': url.split('/')[-1] or url  # Use last part of URL as title, or full URL if empty
            })
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search with query using an inverted index.")
    parser.add_argument(
        "terms",
        nargs="+",
        help="The query terms to search for in the inverted index.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="The limit for the number of results (default: 5).",
    )

    args = parser.parse_args()
    search_with_query(args.limit, *args.terms)