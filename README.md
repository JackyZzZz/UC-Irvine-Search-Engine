## UC Irvine Search Engine

A specialized search engine that indexes and enables searching across UC Irvine websites. The engine uses TF-IDF scoring combined with PageRank and implements proximity-based scoring for multi-word queries.

### Installation

1. Clone the repository

  ```
  git clone https://github.com/JackyZzZz/cs121-a3.git
  ```

2. Install dependencies
  ```
  pip install -r requirements.txt
  ```

3. Build the Index

  ```
  cd src
  python indexer.py
  ```

4. Merge the Index

  ```
  python merger.py
  ```

5. Running the Web Interface

  ```
  cd interface
  python app.py
  ```

Access the search engine at http://localhost:5000

### Home Page
![Home Page](https://github.com/JackyZzZz/cs121-a3/blob/main/assets/home.png)

### Result Page
![Result Page](https://github.com/JackyZzZz/cs121-a3/blob/main/assets/results.png)
