import arxiv
import re
from .base_searcher import BaseSearcher

class ArxivSearcher(BaseSearcher):
    """
    Searcher implementation for the Arxiv API.
    """
    def __init__(self):
        super().__init__()
        self.client = arxiv.Client()

    def _format_query(self, query: str) -> str:
        # Remove asterisks since Arxiv doesn't support them inside phrases
        query = query.replace('*', '')

        # Function to process each matched term
        def replacer(match):
            term = match.group(0)
            if term in ("AND", "OR", "NOT", "ANDNOT", "TO"):
                return term
            if term.startswith('all:'):
                return term
            return f'all:{term}'

        # Match double-quoted phrases or sequences of alphanumeric chars and dashes
        pattern = r'("[^"]+"|[A-Za-z0-9_\-]+)'
        
        # Substitute words/phrases using the replacer function
        formatted_query = re.sub(pattern, replacer, query)
        
        return formatted_query

    def search(self, query: str, max_results: int = 2000):
        formatted_query = self._format_query(query)
        print(f"Arxiv formatted query: {formatted_query}")
        
        search_obj = arxiv.Search(
            query=formatted_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        self.results = list(self.client.results(search_obj))
        return self.results

    def save_results(self, filename: str):
        if not self.results:
            print("No Arxiv results to save. Run a search first.")
            return

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Total number of results: {len(self.results)}\n\n")
            f.write("Titles of first 10 papers:\n")
            for i, r in enumerate(self.results[:10]):
                f.write(f"{i+1}. {r.title}\n")
            
            f.write("\n\nFull results details:\n")
            for i, r in enumerate(self.results):
                f.write(f"--- Paper {i+1} ---\n")
                f.write(f"Title: {r.title}\n")
                f.write(f"Authors: {', '.join(a.name for a in r.authors)}\n")
                f.write(f"Published: {r.published.strftime('%Y-%m-%d')}\n")
                f.write(f"URL: {r.entry_id}\n")
                f.write(f"Summary: {r.summary}\n\n")
