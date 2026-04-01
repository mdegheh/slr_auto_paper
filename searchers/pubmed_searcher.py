import os
import requests
import time
from .base_searcher import BaseSearcher

class PubmedSearcher(BaseSearcher):
    """
    Searcher implementation for the PubMed (NCBI E-utilities) API.
    """
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("PUBMED_API_KEY")

    def search(self, query: str, max_results: int = 2000):
        # Note: PubMed API works globally with or without an API key, 
        # but the key increases the rate limit from 3 requests/sec to 10 requests/sec.
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        
        safe_max = min(max_results, 10000) 
        
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": safe_max
        }
        
        if self.api_key and self.api_key != "your_pubmed_api_key_here":
            search_params["api_key"] = self.api_key
            
        try:
            search_res = requests.get(search_url, params=search_params)
            search_res.raise_for_status()
            search_data = search_res.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return []
                
        except Exception as e:
            print(f"PubMed esearch failed: {e}")
            if 'search_res' in locals() and search_res is not None:
                print(search_res.text)
            return []

        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        self.results = []
        
        chunk_size = 200
        for i in range(0, len(id_list), chunk_size):
            chunk_ids = id_list[i:i + chunk_size]
            summary_params = {
                "db": "pubmed",
                "id": ",".join(chunk_ids),
                "retmode": "json"
            }
            if self.api_key and self.api_key != "your_pubmed_api_key_here":
                summary_params["api_key"] = self.api_key
                
            try:
                # Add a brief sleep to respect NCBI's rate limits
                time.sleep(0.35 if not self.api_key or self.api_key == "your_pubmed_api_key_here" else 0.1)
                
                # Always use POST for fetching large batches of IDs
                sum_res = requests.post(summary_url, data=summary_params)
                sum_res.raise_for_status()
                sum_data = sum_res.json()
                
                result_map = sum_data.get("result", {})
                uids = result_map.get("uids", [])
                
                for uid in uids:
                    record = result_map.get(uid)
                    if record:
                        self.results.append(record)
                        
            except Exception as e:
                print(f"PubMed esummary failed at chunk {i}: {e}")
                break
                
        return self.results

    def save_results(self, filename: str):
        if not self.results:
            print("No PubMed results to save.")
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
                
                authors = r.get('authors', [])
                author_names = [a.get('name', 'Unknown') for a in authors if isinstance(a, dict)]
                f.write(f"Authors: {', '.join(author_names) if author_names else 'Unknown'}\n")
                
                f.write(f"Published: {r.get('pubdate', 'Unknown Date')}\n")
                f.write(f"Journal: {r.get('fulljournalname', 'Unknown')}\n")
                
                article_ids = r.get('articleids', [])
                doi = "No DOI"
                for aid in article_ids:
                    if aid.get('idtype') == 'doi':
                        doi = aid.get('value')
                        break
                f.write(f"DOI: {doi}\n")
                
                uid = r.get('uid')
                url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/" if uid else "No URL"
                f.write(f"URL: {url}\n")
                
                f.write(f"Summary: Available in PubMed search engine via the URL.\n\n")
