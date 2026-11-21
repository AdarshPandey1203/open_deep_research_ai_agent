import re
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_text(url: str, max_chars: int = 12000) -> str:
    """
    Safely scrapes and cleans readable text from a web page URL.
    Removes ads, scripts, navigations, and excessive boilerplate.
    """
    if not url or not url.startswith(("http://", "https://")):
        return ""

    try:
        response = requests.get(url, headers=HEADERS, timeout=12)
        if response.status_code != 200:
            logger.warning(f"Failed to scrape {url}: HTTP {response.status_code}")
            return ""

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove non-content elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript", "svg", "iframe"]):
            element.decompose()

        # Extract text from main container if available, otherwise whole body
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        raw_text = main_content.get_text(separator=' ') if main_content else soup.get_text(separator=' ')

        # Clean excess whitespaces and empty lines
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines)
        cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()

        if len(cleaned_text) > max_chars:
            cleaned_text = cleaned_text[:max_chars] + f"\n\n[... Truncated from original {len(cleaned_text)} characters for context efficiency ...]"

        return cleaned_text

    except requests.exceptions.RequestException as e:
        logger.warning(f"Network error scraping {url}: {e}")
        return ""
    except Exception as e:
        logger.warning(f"Unexpected error scraping {url}: {e}")
        return ""
