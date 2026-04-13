import os
import requests
from .base_searcher import BaseSearcher


class ScopusSearcher(BaseSearcher):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("SCOPUS_API_KEY")

    def _format_query(self, query: str, subject_area: str = None) -> str:
        query = query.strip()
        upper_query = query.upper()

        if upper_query.startswith("TITLE-ABS-KEY(") or upper_query.startswith("ALL("):
            formatted_query = query
        else:
            formatted_query = f"TITLE-ABS-KEY({query})"

        if subject_area:
            formatted_query += f" AND SUBJAREA({subject_area})"

        print(f"Scopus formatted query: {formatted_query}")
        return formatted_query

    def search(self, query: str, max_results: int = 2000, subject_area: str = None):
        print("DEBUG: NEW scopus_searcher.py loaded")

        if not self.api_key or self.api_key == "your_scopus_api_key_here":
            print("Valid SCOPUS_API_KEY is missing. Cannot perform search.")
            return []

        url = "https://api.elsevier.com/content/search/scopus"
        self.results = []
        start = 0

        headers = {
            "Accept": "application/json",
            "X-ELS-APIKey": self.api_key
        }

        formatted_query = self._format_query(query, subject_area)

        while len(self.results) < max_results:
            fetch_size = min(25, max_results - len(self.results))

            params = {
                "query": formatted_query,
                "count": fetch_size,
                "start": start
            }

            response = None
            try:
                response = requests.get(url, headers=headers, params=params, timeout=60)
                response.raise_for_status()
                data = response.json()

                search_results = data.get("search-results", {})
                entries = search_results.get("entry", [])

                if not entries:
                    break

                self.results.extend(entries)

                total_results_str = search_results.get("opensearch:totalResults", "0")
                total_results = int(total_results_str) if total_results_str.isdigit() else 0

                if len(self.results) >= total_results:
                    break

                start += len(entries)

            except requests.exceptions.RequestException as e:
                print(f"Scopus API request failed: {e}")
                if response is not None:
                    print(response.text)
                break

        return self.results

    def save_results(self, filename: str):
        if not self.results:
            print("No Scopus results to save.")
            return

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Total number of results: {len(self.results)}\n\n")
            f.write("Titles of first 10 papers:\n")
            for i, r in enumerate(self.results[:10]):
                f.write(f"{i+1}. {r.get('dc:title', 'No Title')}\n")

            f.write("\n\nFull results details:\n")
            for i, r in enumerate(self.results):
                f.write(f"--- Paper {i+1} ---\n")
                f.write(f"Title: {r.get('dc:title', 'No Title')}\n")
                f.write(f"Authors: {r.get('dc:creator', 'Unknown')}\n")
                f.write(f"Published: {r.get('prism:coverDate', 'Unknown Date')}\n")
                f.write(f"Journal: {r.get('prism:publicationName', 'Unknown')}\n")
                f.write(f"DOI: {r.get('prism:doi', 'No DOI')}\n")

                links = r.get("link", [])
                url = "No URL"
                if isinstance(links, list):
                    for link in links:
                        if link.get("@ref") == "scopus":
                            url = link.get("@href", url)
                            break

                f.write(f"URL: {url}\n")
                f.write(f"Summary: {r.get('dc:description', 'No Summary provided in search results.')}\n\n")
                