import json
import os
from config import LINKS_FILE, DOC_MAPPING_FILE, PAGERANK_FILE

def compute_pagerank(links_graph, damping=0.85, max_iterations=100, tolerance=1.0e-6):
    doc_ids = list(links_graph.keys())
    n = len(doc_ids)
    if n == 0:
        return {}

    # Initialize pagerank values
    pr_values = {doc_id: 1.0 / n for doc_id in doc_ids}

    # Precompute out-degree
    out_degree = {doc_id: len(links_graph[doc_id]) for doc_id in doc_ids}
    dangling_nodes = [doc for doc, deg in out_degree.items() if deg == 0]

    # Precompute inbound links
    inbound_links = {doc_id: [] for doc_id in doc_ids}
    for doc_id, outlinks in links_graph.items():
        for target in outlinks:
            inbound_links[target].append(doc_id)

    for iteration in range(max_iterations):
        prev_pr = pr_values.copy()
        dangling_sum = sum(prev_pr[d] for d in dangling_nodes)

        for doc_id in doc_ids:
            rank = (1 - damping) / n
            rank += damping * (dangling_sum / n)
            for in_doc in inbound_links[doc_id]:
                rank += damping * (prev_pr[in_doc] / out_degree[in_doc])
            pr_values[doc_id] = rank

        diff = sum(abs(pr_values[d] - prev_pr[d]) for d in doc_ids)
        if diff < tolerance:
            break

    return pr_values

def main():
    
    if not os.path.exists(LINKS_FILE):
        raise FileNotFoundError(f"{LINKS_FILE} not found.")

    with open(LINKS_FILE, 'r', encoding='utf-8') as f:
        links_graph = json.load(f)

    # Convert keys and their list items to integers
    links_graph = {int(k): [int(x) for x in v] for k, v in links_graph.items()}

    # Remove self-links
    for doc_id in list(links_graph.keys()):
        links_graph[doc_id] = [x for x in links_graph[doc_id] if x != doc_id]

    # Ensure that every target node is present in the graph
    all_targets = {t for targets in links_graph.values() for t in targets}
    for t in all_targets:
        if t not in links_graph:
            # Add this missing node with no outlinks
            links_graph[t] = []

    pagerank_scores = compute_pagerank(links_graph)

    with open(PAGERANK_FILE, 'w', encoding='utf-8') as f:
        json.dump(pagerank_scores, f, indent=2)

if __name__ == "__main__":
    main()
