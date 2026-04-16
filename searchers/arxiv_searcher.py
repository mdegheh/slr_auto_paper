import arxiv
from .base_searcher import BaseSearcher
from main import filter_last_10_years 

class ArxivSearcher(BaseSearcher):
    def __init__(self):
        super().__init__()
        self.client = arxiv.Client()

    def _format_query(self, query: str) -> str:
        query = query.strip()

        if any(prefix in query for prefix in ("all:", "ti:", "au:", "abs:", "cat:", "jr:", "rn:", "id:")):
            return query.replace("*", "")

        cleaned = query.replace('"', "").replace("*", "")
        return f'all:"{cleaned}"'

    def search(self, query: str, max_results: int = 2000):
        print("DEBUG: NEW arxiv_searcher.py loaded")
        formatted_query = self._format_query(query)
        print(f"Arxiv formatted query: {formatted_query}")

        search_obj = arxiv.Search(
            query=formatted_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        self.results = list(self.client.results(search_obj))
        self.results = filter_last_10_years(results=self.results)
        return self.results

    def save_results(self, filename: str):
        if not self.results:
            print("No Arxiv results to save. Run a search first.")
            return

        with open(filename, "w", encoding="utf-8") as f:
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
                