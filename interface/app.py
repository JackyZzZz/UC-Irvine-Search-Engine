from flask import Flask, render_template, request
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from search import search_with_query

app = Flask(__name__)

# Simulated search results (replace with your actual search logic)
def perform_search(query):
    # Split the query into individual terms and pass them as separate arguments
    query_terms = query.split()
    return search_with_query(5, *query_terms)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        results = perform_search(query)
    else:
        results = []
    return render_template('results.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)