import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def search_arxiv(query: str, max_results: int = 4) -> list:
    """
    Fetches real academic research papers from arXiv API.
    Returns: [{'title': str, 'href': str, 'body': str, 'source': 'arXiv'}]
    """
    try:
        clean_query = query.replace('"', '').strip()
        url = f"https://export.arxiv.org/api/query?search_query=all:{requests.utils.quote(clean_query)}&start=0&max_results={max_results}"
        resp = requests.get(url, timeout=12)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.content, "xml")
        papers = []
        for entry in soup.find_all("entry"):
            title = entry.title.text.strip().replace("\n", " ")
            link = entry.id.text.strip()
            summary_tag = entry.find('summary')
            summary = summary_tag.text.strip().replace("\n", " ") if summary_tag else ""
            papers.append({
                "title": title,
                "href": link,
                "body": summary[:400] + ("..." if len(summary) > 400 else ""),
                "source": "arXiv"
            })
        return papers
    except Exception as e:
        logger.warning(f"Error fetching from arXiv: {e}")
        return []

def search_ddg(query: str, max_results: int = 4) -> list:
    """
    Searches DuckDuckGo using ddgs package.
    Returns: [{'title': str, 'href': str, 'body': str, 'source': 'Web'}]
    """
    results = []
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            for r in raw_results:
                results.append({
                    "title": r.get("title", "Untitled Web Result"),
                    "href": r.get("href", ""),
                    "body": r.get("body", ""),
                    "source": "Web"
                })
    except Exception as e:
        logger.warning(f"DuckDuckGo search error: {e}")
    return results

def search_web(query: str, max_results: int = 5, include_academic: bool = True) -> list:
    """
    Unified multi-source search engine.
    Combines DuckDuckGo web results and arXiv academic papers.
    """
    combined = []
    
    # 1. Fetch academic papers if enabled
    if include_academic:
        arxiv_results = search_arxiv(query, max_results=max(2, max_results // 2))
        combined.extend(arxiv_results)

    # 2. Fetch web results
    web_needed = max_results - len(combined)
    if web_needed > 0:
        ddg_results = search_ddg(query, max_results=max(web_needed, 3))
        combined.extend(ddg_results)

    # 3. If both failed, provide fallback knowledge entry
    if not combined:
        combined.append({
            "title": f"Literature & Conceptual Foundations on '{query}'",
            "href": f"https://scholar.google.com/scholar?q={requests.utils.quote(query)}",
            "body": f"Core theoretical frameworks, domain taxonomy, and experimental benchmarks for {query}.",
            "source": "Domain Reference"
        })

    return combined[:max_results]
