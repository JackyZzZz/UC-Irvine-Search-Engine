import re
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from collections import defaultdict

class Tokenizer:
    def __init__(self):
        self.ps = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        self.title_weight = 3.0
        self.h1_weight = 2.5
        self.h2_weight = 2.0
        self.h3_weight = 1.5
        self.bold_weight = 1.5
        self.main_weight = 1.0  

    def tokenize_with_weights(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        for tag in soup(['script', 'style', 'footer', 'nav', 'meta', 'link']):
            tag.decompose()
        
        title_text = ' '.join(t.get_text() for t in soup.find_all('title'))
        h1_text = ' '.join(t.get_text() for t in soup.find_all('h1'))
        h2_text = ' '.join(t.get_text() for t in soup.find_all('h2'))
        h3_text = ' '.join(t.get_text() for t in soup.find_all('h3'))
        bold_text = ' '.join(t.get_text() for t in soup.find_all(['b', 'strong']))

        main_text = soup.get_text()


        def tokenize_and_filter(text):
            tokens = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
            tokens = [tok for tok in tokens if tok not in self.stop_words]
            tokens = [self.ps.stem(tok) for tok in tokens]
            return tokens

        title_tokens = tokenize_and_filter(title_text)
        h1_tokens = tokenize_and_filter(h1_text)
        h2_tokens = tokenize_and_filter(h2_text)
        h3_tokens = tokenize_and_filter(h3_text)
        bold_tokens = tokenize_and_filter(bold_text)
        main_tokens = tokenize_and_filter(main_text)

        weighted_freq = defaultdict(float)

        for t in main_tokens:
            weighted_freq[t] += self.main_weight
        for t in bold_tokens:
            weighted_freq[t] += self.bold_weight
        for t in h3_tokens:
            weighted_freq[t] += self.h3_weight
        for t in h2_tokens:
            weighted_freq[t] += self.h2_weight
        for t in h1_tokens:
            weighted_freq[t] += self.h1_weight
        for t in title_tokens:
            weighted_freq[t] += self.title_weight

        return dict(weighted_freq)

