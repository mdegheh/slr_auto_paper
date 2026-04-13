import os
from dotenv import load_dotenv
from searchers import (
    ArxivSearcher,
    IEEESearcher,
    ScopusSearcher,
    WosSearcher,
    PubmedSearcher,
    OpenAlexSearcher,
)
import searchers.arxiv_searcher
import searchers.scopus_searcher

print("Arxiv module file:", searchers.arxiv_searcher.__file__)
print("Scopus module file:", searchers.scopus_searcher.__file__)

def main():
    load_dotenv()

    # Generic query for searchers that expect a plain Boolean string
    query_str = (
        '("large language model*" OR "LLM*" OR "autonomous agent*" OR '
        '"multi-agent*" OR "AI agent*") AND '
        '("code repositor*" OR "source code" OR "scientific paper*" OR '
        '"executable paper*" OR "research artifact*") AND '
        '("reproducib*" OR "code execution" OR "dependency resolution" OR '
        '"environment synthesis" OR "dynamic analysis" OR "runtime profiling" OR '
        '"sandboxing" OR "automated execution" OR "environment setup" OR '
        '"containerization" OR "code repair" OR "code generation")'
    )

    # arXiv query must already be fully fielded.
    # arXiv supports field prefixes like all: and Boolean grouping. :contentReference[oaicite:2]{index=2}
    arxiv_query_str = (
        '('
        'all:"large language model" OR all:LLM OR '
        'all:"autonomous agent" OR all:"multi-agent" OR '
        'all:"AI agent" OR '
        'all:"code generation" OR all:"program synthesis"'
        ') AND ('
        'all:"source code" OR all:"code repository" OR '
        'all:"research artifact" OR all:"software artifact" OR '
        'all:"scientific paper" OR all:"executable paper"'
        #'all:"experiment" OR all:"workflow"'
        ') AND ('
        'all:reproducib* OR '
        'all:"code execution" OR all:"execution" OR '
        'all:"dependency resolution" OR all:dependency OR '
        'all:"environment setup" OR '
        #'all:environment OR all:docker OR all:repair OR '
        'all:containerization OR '
        'all:"repository repair"'
        ')'
    )

    scopus_query_str = (
        'TITLE-ABS-KEY(('
        '"large language model" OR "large language models" OR '
        'LLM OR LLMs OR '
        '"autonomous agent" OR "autonomous agents" OR '
        '"multi-agent" OR '
        '"AI agent" OR "AI agents" OR '
        '"code generation" OR "program synthesis"'
        ') AND ('
        '"source code" OR "code repository" OR "code repositories" OR '
        '"research artifact" OR "research artifacts" OR '
        '"software artifact" OR "software artifacts" OR '
        '"scientific paper" OR "scientific papers" OR '
        '"executable paper" OR "executable papers"'
        ') AND ('
        'reproducib* OR '
        '"code execution" OR '
        '"dependency resolution" OR '
        '"environment setup" OR '
        'containerization OR '
        '"repository repair"'
        '))'
    )

    ieee_query_str = (
        '("large language model" OR "large language models" OR '
        #'LLM OR LLMs OR '
        #'"autonomous agent" OR "autonomous agents" OR '
        #'"multi-agent" OR '
        #'"AI agent" OR "AI agents" OR '
        #'"code generation" OR "program synthesis") AND '
        #'("source code" OR "code repository" OR "code repositories" OR '
        #'"research artifact" OR "research artifacts" OR '
        #'"software artifact" OR "software artifacts" OR '
        '"scientific paper" OR "scientific papers" OR '
        '"executable paper" OR "executable papers") AND '
        '(reproducibility OR '
        #'"code execution" OR '
        #'"dependency resolution" OR '
        #'"environment setup" OR '
        #'containerization OR '
        '"repository repair")'
    )

    base_output_dir = "Search Query Results"
    os.makedirs(base_output_dir, exist_ok=True)

    existing_dirs = [
        d for d in os.listdir(base_output_dir)
        if os.path.isdir(os.path.join(base_output_dir, d)) and d.startswith("Query_")
    ]

    max_num = 0
    for d in existing_dirs:
        try:
            num = int(d.split("_")[1])
            max_num = max(max_num, num)
        except (IndexError, ValueError):
            pass

    query_num = max_num + 1
    output_dir = os.path.join(base_output_dir, f"Query_{query_num}")
    os.makedirs(output_dir, exist_ok=True)

    summary_file = os.path.join(output_dir, "summary.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("Search Query Used\n")
        f.write("-" * 50 + "\n")
        f.write(f"Generic query:\n{query_str}\n\n")
        f.write(f"arXiv query:\n{arxiv_query_str}\n\n")
        f.write(f"Scopus query:\n{scopus_query_str}\n")
        f.write("-" * 50 + "\n\n")

    searchers = [
        #ArxivSearcher(),
        IEEESearcher(),
        #ScopusSearcher(),
        # WosSearcher(),
        PubmedSearcher(),
        # OpenAlexSearcher(),
    ]

    for searcher in searchers:
        name = searcher.__class__.__name__
        print(f"\n--- Running search using {name} ---")

        try:
            if name == "ArxivSearcher":
                results = searcher.search(query=arxiv_query_str)
            elif name == "ScopusSearcher":
                results = searcher.search(query=scopus_query_str)
            elif searcher.__class__.__name__ == 'IEEESearcher':
                results = searcher.search(query=ieee_query_str)
            else:
                results = searcher.search(query=query_str)

            print(f"{name} Total results found: {len(results)}")

            with open(summary_file, "a", encoding="utf-8") as f:
                f.write(f"{name} Results: {len(results)}\n")

            filename = os.path.join(output_dir, f"{name.lower()}_results.txt")
            searcher.save_results(filename)
            print(f"Finished writing results to {filename}")

        except Exception as e:
            print('AAAAA')
            print(f"API request failed: {e}")
            if response is not None:
                print("Status code:", response.status_code)
                print("Response body:", response.text[:2000])
            break


if __name__ == "__main__":
    main()
