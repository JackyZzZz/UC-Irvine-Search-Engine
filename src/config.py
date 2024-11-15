import os

# Paths
DATA_DIR = os.path.join('..', 'data/DEV')
PARTIAL_INDEX_DIR = os.path.join('..', 'partial_indexes')
FINAL_INDEX_DIR = os.path.join('..', 'final_index')
DOC_MAPPING_FILE = os.path.join('..', 'doc_mapping.json')
LOG_FILE = os.path.join('..', 'indexer.log')

# Indexing Parameters
BATCH_SIZE = 10000  # Number of documents per partial index

# Ensure directories exist
os.makedirs(PARTIAL_INDEX_DIR, exist_ok=True)
os.makedirs(FINAL_INDEX_DIR, exist_ok=True)
