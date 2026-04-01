# SLR Auto Paper Searcher

A Python tool to automatically query multiple academic databases (Arxiv, IEEE Xplore, Scopus, Web of Science) and aggregate paper metadata for Systematic Literature Reviews (SLR).

## Setup

1. **Install Dependencies:**
   ```bash
   pip install arxiv requests python-dotenv
   ```
2. **Configure API Keys:**
   Create a `.env` file in the root directory (use `.env.example` as a template) and add your keys:
   ```env
   IEEE_API_KEY=your_key_here
   SCOPUS_API_KEY=your_key_here
   WOS_API_KEY=your_key_here
   ```

## Usage

1. Open `main.py` and modify the `query_str` with your search terms.
2. Uncomment the specific academic searchers you want to run inside the `searchers` list.
3. Execute the script:
   ```bash
   python main.py
   ```

Results will be paginated, downloaded, and saved as text files inside the `Search Query Results/` directory.

## Supported Databases
- **Arxiv**
- **IEEE Xplore** (Metadata Search API)
- **Scopus** (Elsevier Search API)
- **Web of Science** (Clarivate Search API)