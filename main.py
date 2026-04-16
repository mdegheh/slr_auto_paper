import os
from dotenv import load_dotenv
from datetime import datetime
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


def extract_year(r):
    """
    Extract publication year from different result formats.
    Returns int or None.
    """

    # arXiv object
    if hasattr(r, "published"):
        return r.published.year

    # Scopus
    if isinstance(r, dict) and "prism:coverDate" in r:
        try:
            return int(r["prism:coverDate"][:4])
        except:
            return None

    # IEEE
    if isinstance(r, dict) and "publication_year" in r:
        try:
            return int(r["publication_year"])
        except:
            return None

    # PubMed (depends on your implementation)
    if isinstance(r, dict):
        if "pubdate" in r:
            try:
                return int(r["pubdate"][:4])
            except:
                return None

    return None

def filter_last_years(results):
    period = 10          # Last 10 years are considered
    cutoff = datetime.now().year - period
    filtered = []

    for r in results:
        year = extract_year(r)

        if year is not None and year >= cutoff:
            filtered.append(r)

    return filtered

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
    arxiv_query_str = (
        '('
        '(ti:"large language model" OR abs:"large language model") OR '
        '(ti:LLM OR abs:LLM) OR '
        '(ti:"autonomous agent" OR abs:"autonomous agent") OR '
        '(ti:"multi-agent" OR abs:"multi-agent") OR '
        '(ti:"AI agent" OR abs:"AI agent") OR '
        '(ti:"code generation" OR abs:"code generation") OR '
        '(ti:"program synthesis" OR abs:"program synthesis")'
        ') AND ('
        '(ti:"source code" OR abs:"source code") OR '
        '(ti:"code repository" OR abs:"code repository") OR '
        '(ti:"research artifact" OR abs:"research artifact") OR '
        '(ti:"software artifact" OR abs:"software artifact") OR '
        '(ti:"scientific paper" OR abs:"scientific paper") OR '
        '(ti:"executable paper" OR abs:"executable paper")'
        ') AND ('
        'all:reproducib* OR '
        'all:"code execution" OR '
        'all:"dependency resolution" '
        'all:"environment setup" OR '
        'all:containerization OR '
        'all:"repository repair"'
        ')'
        # '(ti:reproducib* OR abs:reproducib*) OR '
        # '(ti:"code execution" OR abs:"code execution") OR '
        # '(ti:"dependency resolution" OR abs:"dependency resolution") OR '
        # '(ti:"environment setup" OR abs:"environment setup") OR '
        # '(ti:containerization OR abs:containerization) OR '
        # '(ti:"repository repair" OR abs:"repository repair")'
        # ')'
    )
    # arxiv_query_str = (
    #     '('
    #     'all:"large language model" OR all:LLM OR '
    #     'all:"autonomous agent" OR all:"multi-agent" OR '
    #     'all:"AI agent" OR '
    #     'all:"code generation" OR all:"program synthesis"'
    #     ') AND ('
    #     'all:"source code" OR all:"code repository" OR '
    #     'all:"research artifact" OR all:"software artifact" OR '
    #     'all:"scientific paper" OR all:"executable paper"'
    #     #'all:"experiment" OR all:"workflow"'
    #     ') AND ('
    #     'all:reproducib* OR '
    #     'all:"code execution" OR all:"execution" OR '
    #     'all:"dependency resolution" OR all:dependency OR '
    #     'all:"environment setup" OR '
    #     #'all:environment OR all:docker OR all:repair OR '
    #     'all:containerization OR '
    #     'all:"repository repair"'
    #     ')'
    # )

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
    scopus_query_str += ' AND PUBYEAR > 2016'

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
        ArxivSearcher(),
        #IEEESearcher(),
        ScopusSearcher(),
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
            print(f"Error running {searcher.__class__.__name__}: {e}")
            with open(summary_file, "a", encoding="utf-8") as f:
                f.write(f"{searcher.__class__.__name__} Results: Error ({e})\n")


if __name__ == "__main__":
    main()
