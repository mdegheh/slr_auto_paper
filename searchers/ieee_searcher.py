import os
import requests
from .base_searcher import BaseSearcher

class IEEESearcher(BaseSearcher):
    """
    Searcher implementation for the IEEE Xplore API.
    """
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("IEEE_API_KEY")

    def search(self, query: str, max_results: int = 2000):
        if not self.api_key:
            print("IEEE_API_KEY is missing. Cannot perform search.")
            return []

        url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
        self.results = []
        start_record = 1
        
        while len(self.results) < max_results:
            # IEEE max_records per request is 200
            fetch_size = min(200, max_results - len(self.results))
            
            params = {
                "apikey": self.api_key,
                "querytext": query,
                "max_records": fetch_size,
                "start_record": start_record
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                articles = data.get('articles', [])
                if not articles:
                    break # No more results
                    
                self.results.extend(articles)
                
                # Check if we've fetched all available records
                total_records = data.get('total_records', 0)
                if len(self.results) >= total_records:
                    break
                    
                start_record += len(articles)
                
            except requests.exceptions.RequestException as e:
                print(f"IEEE API request failed: {e}")
                break
                
        return self.results

    def save_results(self, filename: str):
        if not self.results:
            print("No IEEE results to save.")
            return

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Total number of results: {len(self.results)}\n\n")
            f.write("Titles of first 10 papers:\n")
            for i, r in enumerate(self.results[:10]):
                f.write(f"{i+1}. {r.get('title', 'No Title')}\n")
            
            f.write("\n\nFull results details:\n")
            for i, r in enumerate(self.results):
                f.write(f"--- Paper {i+1} ---\n")
                f.write(f"Title: {r.get('title', 'No Title')}\n")
                
                # Parse authors
                authors_data = r.get('authors', {}).get('authors', [])
                author_names = [a.get('full_name', '') for a in authors_data]
                f.write(f"Authors: {', '.join(author_names)}\n")
                
                f.write(f"Published: {r.get('publication_year', 'Unknown Date')}\n")
                f.write(f"URL: {r.get('document_link', 'No URL')}\n")
                f.write(f"Summary: {r.get('abstract', 'No Summary')}\n\n")
