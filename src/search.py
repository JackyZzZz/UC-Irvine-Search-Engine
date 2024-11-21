import json
import argparse
from nltk.stem import PorterStemmer
from config import FINAL_INDEX_DIR, DOC_MAPPING_FILE


def search_with_query(limit, *args):
    stemer = PorterStemmer()

    # Load the inverted_index
    with open(f"{FINAL_INDEX_DIR}/final_inverted_index.json") as file:
        data = json.load(file)
    
    # Load the doc mapping file
    with open(DOC_MAPPING_FILE) as file:
        map = json.load(file)

    # Stem the query terms first
    stemmed_terms = [stemer.stem(term) for term in args]

    doc_set = set()

    # Get the index set
    for term in stemmed_terms:
        indexes = data.get(term, "Not Found")
        if indexes != "Not Found":
            count = 1
            for index in indexes:
                if count > limit:
                    break
                doc_set.add(index[0])
                count += 1
    
    # Print out the links
    for doc_id in doc_set:
        print(map[f'{doc_id}'])

    


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