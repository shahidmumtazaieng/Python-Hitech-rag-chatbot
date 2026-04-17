"""Web Scraper Service for knowledgebase ingestion."""
import re
import time
import uuid
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set, Optional
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from app.config import get_settings
from app.services.embedding_service import get_embedding_service
from app.services.pinecone_service import get_pinecone_service


@dataclass
class ScrapedPage:
    """Represents a scraped web page."""
    url: str
    title: str
    content: str
    links: List[str]


class ScraperService:
    """Service for scraping websites and ingesting into vector store."""
    
    def __init__(self):
        self.settings = get_settings()
        self.visited_urls: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _is_valid_url(self, url: str, base_domain: str) -> bool:
        """Check if URL should be scraped."""
        parsed = urlparse(url)
        
        # Must be HTTP/HTTPS
        if parsed.scheme not in ('http', 'https'):
            return False
        
        # Must be same domain
        if parsed.netloc != base_domain and not parsed.netloc.endswith('.' + base_domain):
            return False
        
        # Skip common non-content URLs
        skip_patterns = [
            r'\.(pdf|jpg|jpeg|png|gif|css|js|zip|tar|gz|mp4|mp3|avi|mov)$',
            r'/wp-content/uploads/',
            r'/wp-includes/',
            r'/wp-json/',
            r'/feed/',
            r'/rss/',
            r'\?replytocom=',
            r'/wp-login',
            r'/wp-admin',
            r'/cart/',
            r'/checkout/',
            r'/my-account/',
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        return text.strip()
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> str:
        """Extract main content from page."""
        # Try to find main content area
        content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.content',
            '.main-content',
            '#content',
            '#main-content',
            '.entry-content',
            '.post-content',
            '.page-content'
        ]
        
        content = ""
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(separator=' ', strip=True)
                break
        
        # Fallback to body if no content found
        if not content:
            body = soup.find('body')
            if body:
                # Remove navigation, footer, sidebar
                for elem in body.find_all(['nav', 'footer', 'aside', 'header']):
                    elem.decompose()
                content = body.get_text(separator=' ', strip=True)
        
        return self._clean_text(content)
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Fall back to title tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return "Untitled"
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from page."""
        links = []
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            full_url = urljoin(base_url, href)
            links.append(full_url)
        return links
    
    def scrape_page(self, url: str) -> Optional[ScrapedPage]:
        """Scrape a single page."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = self._extract_title(soup)
            content = self._extract_content(soup, url)
            links = self._extract_links(soup, url)
            
            return ScrapedPage(
                url=url,
                title=title,
                content=content,
                links=links
            )
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text] if text.strip() else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence or word boundary
            if end < len(text):
                # Look for sentence ending
                sentence_end = text.rfind('. ', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Fall back to word boundary
                    word_end = text.rfind(' ', start, end)
                    if word_end > start:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def scrape_website(
        self,
        base_url: Optional[str] = None,
        max_pages: Optional[int] = None,
        delay: Optional[float] = None
    ) -> List[ScrapedPage]:
        """
        Scrape entire website starting from base URL.
        
        Args:
            base_url: Starting URL (defaults to settings)
            max_pages: Maximum pages to scrape
            delay: Delay between requests in seconds
            
        Returns:
            List of scraped pages
        """
        base_url = base_url or self.settings.SCRAPE_BASE_URL
        max_pages = max_pages or self.settings.SCRAPE_MAX_PAGES
        delay = delay or self.settings.SCRAPE_DELAY
        
        base_domain = urlparse(base_url).netloc
        to_visit = [base_url]
        scraped_pages = []
        
        print(f"Starting scrape of {base_url}")
        
        while to_visit and len(scraped_pages) < max_pages:
            url = to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
            
            if not self._is_valid_url(url, base_domain):
                continue
            
            print(f"Scraping ({len(scraped_pages) + 1}/{max_pages}): {url}")
            
            page = self.scrape_page(url)
            if page:
                self.visited_urls.add(url)
                scraped_pages.append(page)
                
                # Add new links to visit queue
                for link in page.links:
                    if link not in self.visited_urls and link not in to_visit:
                        if self._is_valid_url(link, base_domain):
                            to_visit.append(link)
            
            # Respect rate limits
            time.sleep(delay)
        
        print(f"Scraped {len(scraped_pages)} pages")
        return scraped_pages
    
    def ingest_to_pinecone(self, pages: List[ScrapedPage]) -> Dict[str, Any]:
        """
        Ingest scraped pages into Pinecone vector store.
        
        Args:
            pages: List of scraped pages
            
        Returns:
            Ingestion statistics
        """
        embedding_service = get_embedding_service()
        pinecone_service = get_pinecone_service()
        
        all_chunks = []
        
        print("Processing and chunking content...")
        for page in pages:
            if not page.content or len(page.content) < 50:
                continue
            
            chunks = self.chunk_text(
                page.content,
                chunk_size=self.settings.CHUNK_SIZE,
                overlap=self.settings.CHUNK_OVERLAP
            )
            
            for idx, chunk_text in enumerate(chunks):
                chunk_doc = {
                    'id': str(uuid.uuid4()),
                    'content': chunk_text,
                    'source': page.url,
                    'title': page.title,
                    'url': page.url,
                    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'chunk_index': idx
                }
                all_chunks.append(chunk_doc)
        
        if not all_chunks:
            return {"status": "error", "message": "No valid content to ingest"}
        
        print(f"Generating embeddings for {len(all_chunks)} chunks...")
        
        # Generate embeddings
        all_chunks = embedding_service.embed_document_chunks(all_chunks, batch_size=8)
        
        print(f"Upserting to Pinecone...")
        
        # Upsert to Pinecone
        result = pinecone_service.upsert_documents(all_chunks)
        
        return {
            "status": "success",
            "pages_scraped": len(pages),
            "chunks_created": len(all_chunks),
            **result
        }
    
    def run_full_ingestion(self) -> Dict[str, Any]:
        """Run complete ingestion pipeline."""
        # Scrape website
        pages = self.scrape_website()
        
        if not pages:
            return {"status": "error", "message": "No pages scraped"}
        
        # Ingest to Pinecone
        result = self.ingest_to_pinecone(pages)
        
        return result


# Global instance
scraper_service = ScraperService()


def get_scraper_service() -> ScraperService:
    """Get the scraper service instance."""
    return scraper_service
