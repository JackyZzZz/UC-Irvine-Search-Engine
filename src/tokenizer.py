import re
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup


class Tokenizer:
    def __init__(self):
        self.ps = PorterStemmer()

    def tokenize_and_stem(self, text):
        #Use BeautifulSoup to parse the text
        soup = BeautifulSoup(text, 'html.parser')
        # Extract alphanumeric tokens
        tokens = re.findall(r'\b[a-zA-Z0-9]+\b', soup.get_text().lower())
        # Stem tokens
        stemmed_tokens = [self.ps.stem(token) for token in tokens]
        return stemmed_tokens
