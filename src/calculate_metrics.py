import os
from utils import load_json, get_file_size_kb
from config import FINAL_INDEX_DIR, DOC_MAPPING_FILE

def calculate_metrics():
    # Number of Indexed Documents
    doc_mapping = load_json(DOC_MAPPING_FILE)
    num_documents = len(doc_mapping)

    # Number of Unique Tokens
    final_index_path = os.path.join(FINAL_INDEX_DIR, 'final_inverted_index.json')
    final_index = load_json(final_index_path)
    num_unique_tokens = len(final_index)

    # Total Size of Index on Disk
    index_size_kb = get_file_size_kb(FINAL_INDEX_DIR)

    # Print Metrics
    print(f"Number of Indexed Documents: {num_documents}")
    print(f"Number of Unique Tokens: {num_unique_tokens}")
    print(f"Total Index Size on Disk: {index_size_kb:.2f} KB")

if __name__ == "__main__":
    calculate_metrics()
