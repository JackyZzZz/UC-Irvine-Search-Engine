import json
from nltk.stem import PorterStemmer
from config import FINAL_INDEX_DIR, DOC_MAPPING_FILE, TOKEN_RETRIEVAL_OFFSET_FILE, PAGERANK_FILE
from parse_file import load_token_data
import time
from itertools import combinations

doc_map = None
stemer = None
token_retrieval_offset_map = None
pagerank_scores = None

def pre_loading_files():
    global doc_map, stemer, token_retrieval_offset_map, pagerank_scores

    stemer = PorterStemmer()

    with open(DOC_MAPPING_FILE, 'r') as file:
        doc_map = json.load(file)

    with open(TOKEN_RETRIEVAL_OFFSET_FILE, 'r') as file:
        token_retrieval_offset_map = json.load(file)

    with open(PAGERANK_FILE, 'r') as file:
        pagerank_scores = json.load(file)

def search_with_query(query, limit=100):
    start_time = time.time()

    global stemer, doc_map, token_retrieval_offset_map, pagerank_scores

    results = []

    stemmed_terms = sorted([stemer.stem(term) for term in query.strip().split()])

    docs_scores_map = {}
    docs_positions_map = {}

    previous_letter = None
    file = None

    for term in stemmed_terms:
        if term not in token_retrieval_offset_map:
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

            if doc_id in docs_scores_map:
                docs_scores_map[doc_id] += tfidf_score
            else:
                docs_scores_map[doc_id] = tfidf_score

            if doc_id not in docs_positions_map:
                docs_positions_map[doc_id] = {}
            docs_positions_map[doc_id][term] = positions

    if file:
        file.close()

    unique_terms = set(stemmed_terms)


    if len(stemmed_terms) > 1 and len(unique_terms) > 1:
        for doc_id in docs_scores_map.keys():

            if doc_id in docs_positions_map and all(term in docs_positions_map[doc_id] for term in unique_terms):
                terms_positions = [docs_positions_map[doc_id][t] for t in unique_terms]

                # Compute minimal pairwise distances between terms
                pairwise_distances = []
                for (pos_a, pos_b) in combinations(terms_positions, 2):
                    i, j = 0, 0
                    local_min_dist = float('inf')
                    while i < len(pos_a) and j < len(pos_b):
                        dist = abs(pos_a[i] - pos_b[j])
                        if dist < local_min_dist:
                            local_min_dist = dist
                        if pos_a[i] < pos_b[j]:
                            i += 1
                        else:
                            j += 1
                    pairwise_distances.append(local_min_dist)

                if pairwise_distances:
                    avg_min_distance = sum(pairwise_distances) / len(pairwise_distances)
                    bonus = 2.0 / (1 + avg_min_distance)
                    docs_scores_map[doc_id] += bonus


    for doc_id in docs_scores_map:
        pr_score = pagerank_scores.get(str(doc_id), 0.0)
        docs_scores_map[doc_id] += pr_score


    if docs_scores_map:
        sorted_results = sorted(docs_scores_map.items(), key=lambda x: x[1], reverse=True)
        sorted_results = sorted_results[:limit]

        excluded_extensions = ('.txt', '.php', '.pdf', ".sql", ".log", ".htm")
        filtered_results = []
        for doc_id, score in sorted_results:
            url = doc_map[str(doc_id)]
            if url.lower().endswith(excluded_extensions) or '?' in url:
                continue
            filtered_results.append((doc_id, score))

        for doc_id, score in filtered_results:
            url = doc_map[str(doc_id)]
            print(url, "(score:", score, ")")
            results.append({
                'url': url,
                'title': url.split('/')[-1] or url
            })

    end_time = time.time()
    print(f'\nThis search took {end_time - start_time} seconds\n')

    return results

if __name__ == "__main__":
    pre_loading_files()
    while True:
        query = input("Please enter your query here:")
        search_with_query(query, limit=100)
