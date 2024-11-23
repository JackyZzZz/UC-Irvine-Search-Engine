import json
import argparse
from nltk.stem import PorterStemmer
from config import FINAL_INDEX_DIR, DOC_MAPPING_FILE


def search_with_query(limit, *args):
    stemer = PorterStemmer()

    # Load the inverted_index and doc mapping
    with open(f"{FINAL_INDEX_DIR}/final_inverted_index.json") as file:
        data = json.load(file)
    with open(DOC_MAPPING_FILE) as file:
        map = json.load(file)

    # Stem the query terms
    stemmed_terms = [stemer.stem(term) for term in args]
    
    # Get document sets for each term
    term_docs = []
    for term in stemmed_terms:
        if term in data:
            docs = set(posting[0] for posting in data[term])
            term_docs.append(docs)
        else:
            return

    # Intersect all document sets
    if term_docs:
        result_set = term_docs[0]
        for docs in term_docs[1:]:
            result_set = result_set.intersection(docs)

        # Calculate scores and deduplicate by base URL
        url_scores = {}  # Dict to store highest score for each base URL
        for doc_id in result_set:
            url = map[str(doc_id)]
            # Remove fragment from URL (everything after #)
            base_url = url.split('#')[0]
            
            # Calculate total frequency for this document
            total_freq = sum(posting[1] for term in stemmed_terms 
                           for posting in data[term] 
                           if posting[0] == doc_id)
            
            # Keep only highest scoring version of each URL
            if base_url not in url_scores or total_freq > url_scores[base_url][1]:
                url_scores[base_url] = (doc_id, total_freq)

        # Sort by frequency and output top k unique results
        results = sorted(url_scores.values(), key=lambda x: x[1], reverse=True)
        for doc_id, _ in results[:limit]:
            print(map[str(doc_id)])


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