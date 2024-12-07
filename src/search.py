import json
import argparse
from nltk.stem import PorterStemmer
from config import FINAL_INDEX_DIR, DOC_MAPPING_FILE
from math import log


def search_with_query(limit, *args):
    stemer = PorterStemmer()
    results = []

    with open(DOC_MAPPING_FILE) as file:
        map = json.load(file)
    
    total_num_docs = len(map)



    # Stem the query terms
    stemmed_terms = sorted([stemer.stem(term) for term in args])

    docs_scores_map = {}
    
    previous_letter = None

    for term in stemmed_terms:
        starting_letter = term.lower()[0]
        if starting_letter != previous_letter:
            with open(f"{FINAL_INDEX_DIR}/{starting_letter}_tokens.json") as file:
                data = json.load(file)
            previous_letter = starting_letter
        if term in data:
            document_frequency = len(data[term])
            for posting in data[term]:
                if posting[0] in docs_scores_map:
                    docs_scores_map[posting[0]] += (1 + log(posting[1])) * (1 + log(total_num_docs/document_frequency))
                else:
                    docs_scores_map[posting[0]] = (1 + log(posting[1])) * (1 + log(total_num_docs/document_frequency))
            else:
                continue

    # Output results
    if docs_scores_map:
        sorted_results = sorted(docs_scores_map.items(), key=lambda x: x[1], reverse=True)
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