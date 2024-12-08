import json
from nltk.stem import PorterStemmer
from config import FINAL_INDEX_DIR, DOC_MAPPING_FILE, TOKEN_RETRIEVAL_OFFSET_FILE
from parse_file import load_token_data
import time

doc_map = None
stemer = None
token_retrieval_offset_map = None

def pre_loading_files():
    global doc_map, stemer, token_retrieval_offset_map

    # stemer for query stemming
    stemer = PorterStemmer()
    
    # Load doc_id -> url mapping
    with open(DOC_MAPPING_FILE, 'r') as file:
        doc_map = json.load(file)

    with open(TOKEN_RETRIEVAL_OFFSET_FILE, 'r') as file:
        token_retrieval_offset_map = json.load(file)

def search_with_query(query, limit = 1000):
    start_time = time.time()

    global stemer, doc_map, token_retrieval_offset_map

    results = []

    # Stem the query terms
    stemmed_terms = sorted([stemer.stem(term) for term in query.strip().split()])

    docs_scores_map = {}
    # We'll store positions as well: docs_positions_map = { doc_id: {term: [positions]} }
    docs_positions_map = {}

    previous_letter = None
    file = None

    # Load postings for each term, sum TF-IDF scores, and collect positions
    for term in stemmed_terms:

        if not term in token_retrieval_offset_map:
            continue
        
        starting_letter = term.lower()[0]

        if starting_letter != previous_letter:
            if file:
                file.close()
            file = open(f"{FINAL_INDEX_DIR}/{starting_letter}_tokens.txt", 'r')
            previous_letter = starting_letter

        for posting in load_token_data(file, token_retrieval_offset_map[term]):
            doc_id = posting[0]
            tfidf_score = posting[1]
            positions = posting[2]

            # Sum TF-IDF
            if doc_id in docs_scores_map:
                docs_scores_map[doc_id] += tfidf_score
            else:
                docs_scores_map[doc_id] = tfidf_score

            # Store positions for each term in docs_positions_map
            if doc_id not in docs_positions_map:
                docs_positions_map[doc_id] = {}
            docs_positions_map[doc_id][term] = positions

    # If there are multiple terms, we’ll consider proximity
    if len(stemmed_terms) > 1:
        # For each doc, compute minimal distance between any pair of terms
        # For simplicity, if there are more than two terms, we can consider pairwise minimum distances
        # and sum or average them. Here, we’ll show a simple example for two terms.
        # If you have N terms, you'd extend this logic to compute a composite proximity measure.
        unique_terms = list(set(stemmed_terms))  # to avoid duplicates if query terms repeat
        if len(unique_terms) >= 2:
            for doc_id in docs_scores_map.keys():
                # Ensure all terms appear in doc
                if all(t in docs_positions_map[doc_id] for t in unique_terms):
                    # Compute min distance between terms
                    # For demonstration, let's say we only handle two terms. For more, you'd generalize.
                    # Example: If we have 2 terms: term1, term2
                    # Find minimal distance between any position of term1 and term2.
                    term_positions = [docs_positions_map[doc_id][t] for t in unique_terms]
                    
                    # If we have more than two terms, you can iterate over pairs.
                    # Here assume just two terms for simplicity:
                    if len(term_positions) == 2:
                        positions_a = term_positions[0]
                        positions_b = term_positions[1]

                        min_distance = float('inf')
                        # Find minimal absolute difference between any position in positions_a and positions_b
                        # Since positions are sorted (they should be as we appended them in order), 
                        # we can do a linear merge to find min distance efficiently.
                        i, j = 0, 0
                        while i < len(positions_a) and j < len(positions_b):
                            dist = abs(positions_a[i] - positions_b[j])
                            if dist < min_distance:
                                min_distance = dist
                            # Move the pointer for whichever list has a smaller position to find a closer match
                            if positions_a[i] < positions_b[j]:
                                i += 1
                            else:
                                j += 1

                        # Apply a proximity bonus.
                        # For example, if min_distance = 0 means same position (which can't happen since different terms),
                        # min_distance = 1 means consecutive words.
                        # Let's say we do: bonus = 2/(1+min_distance)
                        # If terms appear consecutively (min_distance=1), bonus = 2/2=1 extra point
                        # If they're far apart, bonus approaches 0.
                        bonus = 2.0 / (1 + min_distance)
                        docs_scores_map[doc_id] += bonus

                    # If you have more than two terms, you could:
                    # - Compute pairwise distances and average them
                    # - Or find a measure that rewards documents where all terms appear closely together.

    # Sort results by final score (descending)
    if docs_scores_map:
        sorted_results = sorted(docs_scores_map.items(), key=lambda x: x[1], reverse=True)
        # Limit the number of results
        sorted_results = sorted_results[:limit]

        for doc_id, score in sorted_results:
            url = doc_map[str(doc_id)]
            print(url, "(score:", score, ")")
            results.append({
                'url': url,
                'title': url.split('/')[-1] or url
            })
    
    end_time = time.time()

    print(f'\nThis search causes {end_time - start_time} seconds\n')

    return results

if __name__ == "__main__":
    
    pre_loading_files()

    while True:
        query = input("Please enter your query here:")
        search_with_query(query)
