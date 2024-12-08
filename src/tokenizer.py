import re
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
from collections import defaultdict

class Tokenizer:
    def __init__(self):
        self.ps = PorterStemmer()
        
        self.title_weight = 3.0
        self.h1_weight = 2.5
        self.h2_weight = 2.0
        self.h3_weight = 1.5
        self.bold_weight = 1.5
        self.main_weight = 1.0

    def tokenize_and_filter(self, text):
        # Extract alphanumeric tokens and lowercase them
        tokens = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
        # Stem each token
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

        # We'll accumulate token info in a dict: token -> {weight: float, positions: [int]}
        token_data = defaultdict(lambda: {"weight":0.0, "positions":[]})

        for i, t in enumerate(main_tokens):
            occurrence_weight = self.main_weight
            if t in bold_set:
                occurrence_weight += self.bold_weight
            if t in h3_set:
                occurrence_weight += self.h3_weight
            if t in h2_set:
                occurrence_weight += self.h2_weight
            if t in h1_set:
                occurrence_weight += self.h1_weight
            if t in title_set:
                occurrence_weight += self.title_weight

            token_data[t]["weight"] += occurrence_weight
            token_data[t]["positions"].append(i)

        # Convert to the desired format: {token: (total_weight, [positions])}
        result = {tok: (d["weight"], d["positions"]) for tok, d in token_data.items()}
        return result
