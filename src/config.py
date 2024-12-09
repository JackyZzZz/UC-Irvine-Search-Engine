import os

# Paths
DATA_DIR = os.path.join('..', 'data/')
PARTIAL_INDEX_DIR = os.path.join('..', 'partial_indexes')
FINAL_INDEX_DIR = os.path.join('..', 'final_index')
DOC_MAPPING_FILE = os.path.join('..', 'doc_mapping.json')
LOG_FILE = os.path.join('..', 'indexer.log')
LINKS_FILE = os.path.join('..', 'links.json')
IDF_FILE = os.path.join('..', 'idf.json')
DF_FILE = os.path.join("..", 'df.json')
PAGERANK_FILE = os.path.join("..", 'page_rank.json')
TOKEN_RETRIEVAL_OFFSET_FILE = os.path.join("..", 'token_retrieval_offset.json')

# Indexing Parameters
BATCH_SIZE = 6000 # Number of documents per partial index

# Ensure directories exist
os.makedirs(PARTIAL_INDEX_DIR, exist_ok=True)
os.makedirs(FINAL_INDEX_DIR, exist_ok=True)
