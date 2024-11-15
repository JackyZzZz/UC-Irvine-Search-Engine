import re
from nltk.stem import PorterStemmer

class Tokenizer:
    def __init__(self):
        self.ps = PorterStemmer()

    def tokenize_and_stem(self, text):
        # Extract alphanumeric tokens
        tokens = re.findall(r'\b\w+\b', text.lower())
        # Stem tokens
        stemmed_tokens = [self.ps.stem(token) for token in tokens]
        return stemmed_tokens
