import os
import requests
from .base_searcher import BaseSearcher

class WosSearcher(BaseSearcher):
    """
    Searcher implementation for the Web of Science (Clarivate) API.
    """
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("WOS_API_KEY")

    def search(self, query: str, max_results: int = 2000):
        if not self.api_key or self.api_key == "your_wos_api_key_here":
            print("Valid WOS_API_KEY is missing. Cannot perform search.")
            return []

        # WoS Expanded API endpoint
        url = "https://wos-api.clarivate.com/api/wos"
        self.results = []
        first_record = 1
        
        headers = {
            "Accept": "application/json",
            "X-ApiKey": self.api_key
        }
        
        while len(self.results) < max_results:
            fetch_size = min(100, max_results - len(self.results))
            
            params = {
                "databaseId": "WOK",
                "usrqry": query,
                "count": fetch_size,
                "firstRecord": first_record
            }
            
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                records_data = data.get('Data', {}).get('Records', {}).get('records', {}).get('REC', [])
                
                if not records_data:
                    break
                    
                self.results.extend(records_data)
                
                total_results = data.get('QueryResult', {}).get('RecordsFound', 0)
                
                if len(self.results) >= total_results:
                    break
                    
                first_record += len(records_data)
                
            except requests.exceptions.RequestException as e:
                print(f"Web of Science API request failed: {e}")
                if response is not None:
                    print(response.text)
                break
                
        return self.results

    def save_results(self, filename: str):
        if not self.results:
            print("No Web of Science results to save.")
            return

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Total number of results: {len(self.results)}\n\n")
            f.write("Titles of first 10 papers:\n")
            for i, r in enumerate(self.results[:10]):
                # Safely extract title from deeply nested XML-to-JSON structure
                titles = r.get('static_data', {}).get('summary', {}).get('titles', {}).get('title', [])
                paper_title = "No Title"
                if isinstance(titles, list):
                    for t in titles:
                        if t.get('type') == 'item':
                            paper_title = t.get('content', paper_title)
                elif isinstance(titles, dict):
                    paper_title = titles.get('content', paper_title)
                    
                f.write(f"{i+1}. {paper_title}\n")
            
            f.write("\n\nFull results details:\n")
            for i, r in enumerate(self.results):
                f.write(f"--- Paper {i+1} ---\n")
                
                titles = r.get('static_data', {}).get('summary', {}).get('titles', {}).get('title', [])
                paper_title = "No Title"
                if isinstance(titles, list):
                    for t in titles:
                        if t.get('type') == 'item':
                            paper_title = t.get('content', paper_title)
                elif isinstance(titles, dict):
                    paper_title = titles.get('content', paper_title)
                f.write(f"Title: {paper_title}\n")
                
                authors = r.get('static_data', {}).get('summary', {}).get('names', {}).get('name', [])
                author_names = []
                if isinstance(authors, list):
                    for a in authors:
                        author_names.append(a.get('full_name', 'Unknown'))
                elif isinstance(authors, dict):
                    author_names.append(authors.get('full_name', 'Unknown'))
                f.write(f"Authors: {', '.join(author_names) if author_names else 'Unknown'}\n")
                
                pub_info = r.get('static_data', {}).get('summary', {}).get('pub_info', {})
                f.write(f"Published: {pub_info.get('pubyear', 'Unknown Date')}\n")
                
                # Document abstract
                abstract = r.get('static_data', {}).get('fullrecord_metadata', {}).get('abstracts', {}).get('abstract', {}).get('abstract_text', {}).get('p', 'No Summary provided in search results.')
                if isinstance(abstract, list):
                    abstract = " ".join(abstract)
                f.write(f"Summary: {abstract}\n\n")
