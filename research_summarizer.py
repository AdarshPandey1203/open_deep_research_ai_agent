import os
import sys
# Ensure directory of current file is in sys.path for robust imports anywhere
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
import logging
from genai_client import ask_gemini
from scraper import scrape_text
from search_tool import search_web, search_arxiv

logger = logging.getLogger(__name__)

def summarize_research(topic: str, max_papers: int = 5):
    """
    Executes an autonomous Deep Research workflow:
    1. Query Decomposition (Planner)
    2. Multi-source Academic & Web Retrieval (Searcher)
    3. Content Extraction & Scraping (Reader)
    4. Comprehensive Synthesis (Writer)
    5. Actionable Summarization (Summarizer)
    
    Returns:
        tuple: (final_synthesis_markdown, list_of_research_sources)
    """
    topic_clean = topic.strip()
    if not topic_clean:
        return "Please specify a research topic.", []

    logger.info(f"Initiating Deep Research on: {topic_clean}")

    # --- Step 1: Planner Agent ---
    planner_prompt = f"""You are a Lead AI Research Planner. Break down the research topic '{topic_clean}' into 3 precise, academic search queries targeting:
1. Foundational principles and current state-of-the-art
2. Key architectures, algorithms, or methodologies
3. Empirical results, benchmarks, and real-world challenges

Return ONLY the 3 queries, one per line, with no bullets or numbers."""
    
    queries_raw = ask_gemini(planner_prompt)
    queries = [re.sub(r'^\d+[\.\)]\s*', '', q).strip() for q in queries_raw.splitlines() if q.strip()]
    if not queries:
        queries = [f"{topic_clean} state of the art", f"{topic_clean} methodology architecture", f"{topic_clean} benchmarks"]

    # --- Step 2: Searcher Agent ---
    gathered_sources = []
    seen_urls = set()

    # Always fetch direct arXiv academic papers for the topic
    arxiv_papers = search_arxiv(topic_clean, max_results=3)
    for p in arxiv_papers:
        if p['href'] not in seen_urls:
            seen_urls.add(p['href'])
            gathered_sources.append(p)

    # Search for each planned sub-query
    for q in queries[:3]:
        results = search_web(q, max_results=2, include_academic=True)
        for r in results:
            href = r.get('href')
            if href and href not in seen_urls:
                seen_urls.add(href)
                gathered_sources.append(r)

    # Limit to top research sources
    selected_sources = gathered_sources[:max_papers]

    # --- Step 3: Reader / Scraper Agent ---
    accumulated_context = []
    for source in selected_sources:
        title = source.get('title', 'Unknown Title')
        href = source.get('href', '')
        snippet = source.get('body', '')
        source_type = source.get('source', 'Literature')
        
        # If it's an arXiv paper, the abstract in snippet is already high quality
        context_entry = f"### [Source: {source_type}] {title}\nURL: {href}\nAbstract/Snippet: {snippet}"
        
        # Scrape web page if snippet is short and href is not an arXiv PDF
        if source_type == 'Web' and href and not href.endswith('.pdf') and len(snippet) < 200:
            scraped = scrape_text(href, max_chars=3000)
            if scraped:
                context_entry += f"\nDetailed Content:\n{scraped[:2000]}"
                
        accumulated_context.append(context_entry)

    full_research_corpus = "\n\n---\n\n".join(accumulated_context)

    # --- Step 4: Writer / Synthesizer Agent ---
    synthesis_prompt = f"""You are a Principal Scientific Researcher and Academic Writer.
Synthesize the provided research corpus into an exhaustive, rigorous, and beautifully structured research report on: '{topic_clean}'.

Research Corpus:
{full_research_corpus[:16000]}

Format your response in GitHub-flavored Markdown following this exact structure:

# Deep Research Synthesis: {topic_clean}

## 1. Executive Summary
<Concise overview of the domain, theoretical importance, and current landscape.>

## 2. Theoretical Foundations & Key Breakthroughs
<Detailed analysis of core concepts, algorithmic innovations, and recent paradigm shifts.>

## 3. Methodologies & Architectures
<Systematic breakdown of prevailing approaches, computational frameworks, and data pipelines.>

## 4. Critical Findings & Benchmark Comparisons
<Concrete results, performance tradeoffs, accuracy/efficiency comparisons from the literature.>

## 5. Challenges, Ethics & Limitations
<Open bottlenecks, computational constraints, scalability issues, and safety considerations.>

## 6. Future Horizons & Research Opportunities
<Promising unaddressed avenues and emerging directions in this field.>

Ensure the report is rigorous, highly informative, and easy to read.
"""

    report_markdown = ask_gemini(synthesis_prompt)

    # Append citations section with links
    citations_md = "\n\n## 7. Primary Literature & Citations\n"
    for i, s in enumerate(selected_sources, start=1):
        citations_md += f"{i}. **[{s.get('title')}]({s.get('href')})** ({s.get('source', 'Source')})\n   - *Overview*: {s.get('body', '')[:180]}...\n"

    final_report = report_markdown + citations_md

    return final_report, selected_sources
