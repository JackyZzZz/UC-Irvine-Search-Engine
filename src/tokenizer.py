import re
import os
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
from collections import defaultdict

class Tokenizer:
    def __init__(self, stop_words=None):
        self.ps = PorterStemmer()
        
        self.title_weight = 2.0
        self.h1_weight = 2.0
        self.h2_weight = 1.5
        self.h3_weight = 1.5
        self.bold_weight = 1.5
        self.main_weight = 1.0
        
        self.stop_words = stop_words if stop_words else set()

    def tokenize_and_filter(self, text):
        tokens = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
        tokens = [self.ps.stem(tok) for tok in tokens]
        return tokens

    def tokenize_with_positions_and_weights(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted tags
        for tag in soup(['script', 'style', 'footer', 'nav', 'meta', 'link']):
            tag.decompose()

        title_text = ' '.join(t.get_text() for t in soup.find_all('title'))
        h1_text = ' '.join(t.get_text() for t in soup.find_all('h1'))
        h2_text = ' '.join(t.get_text() for t in soup.find_all('h2'))
        h3_text = ' '.join(t.get_text() for t in soup.find_all('h3'))
        bold_text = ' '.join(t.get_text() for t in soup.find_all(['b', 'strong']))
        main_text = soup.get_text()

        # Tokenize each section
        title_tokens = self.tokenize_and_filter(title_text)
        h1_tokens = self.tokenize_and_filter(h1_text)
        h2_tokens = self.tokenize_and_filter(h2_text)
        h3_tokens = self.tokenize_and_filter(h3_text)
        bold_tokens = self.tokenize_and_filter(bold_text)
        main_tokens = self.tokenize_and_filter(main_text)

        title_set = set(title_tokens)
        h1_set = set(h1_tokens)
        h2_set = set(h2_tokens)
        h3_set = set(h3_tokens)
        bold_set = set(bold_tokens)

        token_data = defaultdict(lambda: {"weight":0.0, "positions":[]})

        for i, t in enumerate(main_tokens):
            if t in self.stop_words:
                occurrence_weight = self.main_weight
            else:
                candidate_weights = []
                if t in title_set:
                    candidate_weights.append(self.title_weight)
                if t in h1_set:
                    candidate_weights.append(self.h1_weight)
                if t in h2_set:
                    candidate_weights.append(self.h2_weight)
                if t in h3_set:
                    candidate_weights.append(self.h3_weight)
                if t in bold_set:
                    candidate_weights.append(self.bold_weight)

                if candidate_weights:
                    occurrence_weight = self.main_weight + max(candidate_weights)
                else:
                    occurrence_weight = self.main_weight

            token_data[t]["weight"] += occurrence_weight
            token_data[t]["positions"].append(i)

        result = {tok: (d["weight"], d["positions"]) for tok, d in token_data.items()}
        return result
