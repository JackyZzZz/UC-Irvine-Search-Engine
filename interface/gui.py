import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from search import search_with_query, pre_loading_files

class SearchEngineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CS 121 Search Engine")
        self.root.geometry("800x600")
        
        style = ttk.Style()
        style.configure('Search.TFrame', background='#f0f0f0')
        style.configure('Search.TButton', padding=5)
        
        self.main_frame = ttk.Frame(root, style='Search.TFrame', padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.header = ttk.Label(
            self.main_frame, 
            text="CS 121 Search Engine",
            font=('Arial', 24)
        )
        self.header.pack(pady=20)
        
        self.search_frame = ttk.Frame(self.main_frame)
        self.search_frame.pack(fill=tk.X, pady=10)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            self.search_frame, 
            textvariable=self.search_var,
            width=50
        )
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        self.search_button = ttk.Button(
            self.search_frame,
            text="Search",
            command=self.perform_search,
            style='Search.TButton'
        )
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        self.results_frame = ttk.Frame(self.main_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.scrollbar = ttk.Scrollbar(self.results_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(
            self.results_frame,
            wrap=tk.WORD,
            yscrollcommand=self.scrollbar.set,
            height=20,
            width=70
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.results_text.yview)
        
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        pre_loading_files()

    def perform_search(self):
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        query = self.search_var.get().strip()
        if not query:
            return
        
        results = search_with_query(query)
        
        if results:
            for i, result in enumerate(results, 1):
                url = result['url']
                self.results_text.insert(tk.END, f"{i}. {url}\n\n")
        else:
            self.results_text.insert(tk.END, "No results found.")

def main():
    root = tk.Tk()
    app = SearchEngineGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
