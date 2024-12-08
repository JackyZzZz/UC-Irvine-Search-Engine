import json
import logging
from config import LINKS_FILE, DOC_MAPPING_FILE, PAGERANK_FILE

def compute_pagerank(links_graph, damping=0.85, max_iterations=100, tolerance=1.0e-6):
    """
    Compute PageRank for each document using the power iteration method.

    :param links_graph: dict, doc_id -> list of outlinked doc_ids
    :param damping: The damping factor for PageRank
    :param max_iterations: Maximum number of iterations
    :param tolerance: Convergence threshold
    :return: dict of doc_id -> pagerank score
    """
    # Extract all doc_ids
    doc_ids = list(links_graph.keys())
    n = len(doc_ids)
    if n == 0:
        return {}

    # Initialize pagerank values
    pr_values = {doc_id: 1.0 / n for doc_id in doc_ids}

    # Precompute out-degree for efficiency
    out_degree = {doc_id: len(links) for doc_id, links in links_graph.items()}

    # Handle documents with no outlinks by treating them as linking to all docs (including themselves)
    # or distribute their PR evenly. Another option is to store a separate list of "dangling nodes".
    # For simplicity, we’ll consider dangling pages as linking to all other pages.
    dangling_nodes = [doc for doc, deg in out_degree.items() if deg == 0]

    for iteration in range(max_iterations):
        prev_pr = pr_values.copy()
        # Compute the sum of PR of dangling nodes
        dangling_sum = sum(prev_pr[d] for d in dangling_nodes)

        # Distribute PR
        for doc_id in doc_ids:
            # Base portion from dangling nodes and random jump (teleportation)
            rank = (1 - damping) / n
            rank += damping * (dangling_sum / n)

            # Add contributions from inbound links
            # Inbound links are implicitly defined: any doc that has doc_id in its outlinks
            # Instead of inverting the graph here, we can just loop through links_graph
            # but that would be O(n^2). For large graphs, consider precomputing inbound links.
            # For a small example or a simplified scenario, we can do a direct approach:
            for other_doc in doc_ids:
                if doc_id in links_graph[other_doc] and out_degree[other_doc] > 0:
                    rank += damping * (prev_pr[other_doc] / out_degree[other_doc])

            pr_values[doc_id] = rank

        # Check for convergence
        diff = sum(abs(pr_values[d] - prev_pr[d]) for d in doc_ids)
        if diff < tolerance:
            print(f"PageRank converged after {iteration+1} iterations.")
            break

    return pr_values


def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    # Load link graph
    with open(LINKS_FILE, 'r') as f:
        links_graph = json.load(f)

    # Compute PageRank
    pagerank_scores = compute_pagerank(links_graph)

    # (Optional) you can map doc_ids back to URLs if needed
    # with open(DOC_MAPPING_FILE, 'r') as f:
    #     doc_mapping = json.load(f)
    # url_pagerank = {doc_mapping[str(doc_id)]: score for doc_id, score in pagerank_scores.items()}

    # Save PageRank results
    with open(PAGERANK_FILE, 'w') as f:
        json.dump(pagerank_scores, f, indent=2)
    print(f"PageRank scores saved to {PAGERANK_FILE}")


if __name__ == "__main__":
    main()