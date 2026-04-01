import os
from dotenv import load_dotenv
from searchers import ArxivSearcher, IEEESearcher, ScopusSearcher, WosSearcher, PubmedSearcher

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Define the search query
    query_str = '''("large language model*" OR "LLM*" OR "autonomous agent*" OR "multi-agent*" OR "AI agent*") AND ("code repositor*" OR "source code" OR "scientific paper*" OR "executable paper*" OR "research artifact*") AND ("reproducib*" OR "code execution" OR "dependency resolution" OR "environment synthesis" OR "dynamic analysis" OR "runtime profiling" OR "sandboxing" OR "automated execution" OR "environment setup" OR "containerization" OR "code repair")'''
    
    # Create the output directory if it does not exist
    output_dir = "Search Query Results"
    os.makedirs(output_dir, exist_ok=True)
    
    # We can add more searchers here in the future
    searchers = [
        # ArxivSearcher(),
        # IEEESearcher(),  ---- api key is waiting status
        # ScopusSearcher(), 
        # WosSearcher(),   ---- missing api key. it is paid
        PubmedSearcher()
    ]
    
    for searcher in searchers:
        print(f"\n--- Running search using {searcher.__class__.__name__} ---")
        
        # Search the database
        results = searcher.search(query=query_str)
        print(f"{searcher.__class__.__name__} Total results found: {len(results)}")
        
        # Define output filename based on the searcher class name, inside the new folder
        filename = os.path.join(output_dir, f"{searcher.__class__.__name__.lower()}_results.txt")
        
        # Save results to a text file
        searcher.save_results(filename)
        print(f"Finished writing results to {filename}")

if __name__ == "__main__":
    main()
