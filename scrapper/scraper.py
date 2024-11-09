import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional
import re
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

class AdvancedScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        self.contact_keywords = ['contact', 'about', 'reach', 'connect']
        self.social_patterns = {
            'facebook': r'facebook\.com|fb\.com',
            'twitter': r'twitter\.com|x\.com',
            'linkedin': r'linkedin\.com',
            'instagram': r'instagram\.com',
            'youtube': r'youtube\.com'
        }
        self.wait_time = 10  # Seconds to wait for dynamic content

    def get_page_content(self, url: str, driver) -> Optional[BeautifulSoup]:
        """Fetch page content with improved handling of dynamic content."""
        try:
            # Wait for the body to be present
            WebDriverWait(driver, self.wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for dynamic content to load
            try:
                WebDriverWait(driver, self.wait_time).until(
                    lambda d: len(d.page_source) > 1000  # Basic check for content load
                )
            except TimeoutException:
                pass  # Continue even if timeout occurs
            
            # Get the rendered page source
            page_source = driver.page_source
            return BeautifulSoup(page_source, 'html.parser')
            
        except Exception as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None

    def find_contact_page(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Find and return the contact page URL."""
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            
            for keyword in self.contact_keywords:
                if keyword in href or keyword in text:
                    return urljoin(base_url, link['href'])
        return None

    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses using improved regex pattern."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return list(set(re.findall(email_pattern, text)))

    def extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers using multiple regex patterns."""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # International
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',                    # US/Canada
            r'\d{3}[-.\s]?\d{4}[-.\s]?\d{4}'                          # Other formats
        ]
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        return list(set(phones))

    def extract_social_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Extract social media links using multiple methods."""
        social_links = {}
        
        # Method 1: Check meta tags
        for meta in soup.find_all('meta', property=True):
            prop = meta.get('property', '').lower()
            if 'og:' in prop and 'url' in prop:
                content = meta.get('content', '')
                for platform, pattern in self.social_patterns.items():
                    if re.search(pattern, content):
                        social_links[platform] = content

        # Method 2: Check common social media icons/links
        icon_classes = ['fa-facebook', 'fa-twitter', 'fa-linkedin', 'fa-instagram', 'fa-youtube']
        for icon_class in icon_classes:
            icon = soup.find('i', class_=icon_class)
            if icon and icon.find_parent('a'):
                href = icon.find_parent('a').get('href')
                if href:
                    platform = icon_class.replace('fa-', '')
                    social_links[platform] = urljoin(base_url, href)

        # Method 3: Check footer links
        footer = soup.find('footer')
        if footer:
            for link in footer.find_all('a', href=True):
                href = link['href'].lower()
                for platform, pattern in self.social_patterns.items():
                    if re.search(pattern, href) and platform not in social_links:
                        social_links[platform] = urljoin(base_url, href)

        return social_links

    def scrape_website(self, url: str, driver, sections: List[str] = None) -> Dict[str, any]:
        """Main scraping function with enhanced content extraction."""
        if sections is None:
            sections = ['title', 'headings', 'paragraphs']

        base_url = url
        results = {
            'content': '',
            'soup': None,
            'contact_info': {'emails': [], 'phones': []},
            'social_links': {},
            'metadata': {}
        }

        # Get main page content using Selenium
        main_soup = self.get_page_content(url, driver)
        if not main_soup:
            return results

        results['soup'] = main_soup
        
        # Extract content with improved selectors
        content_parts = []
        
        if 'title' in sections and main_soup.title:
            content_parts.append(main_soup.title.get_text())

        # Get meta description
        meta_desc = main_soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            content_parts.append(meta_desc['content'])

        # Get all visible text from main content areas
        main_content = main_soup.find_all(['main', 'article', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['content', 'main', 'article']))
        for content in main_content:
            # Get headings
            if 'headings' in sections:
                headings = content.find_all(['h1', 'h2', 'h3'])
                content_parts.extend([h.get_text(strip=True) for h in headings if h.get_text(strip=True)])
            
            # Get paragraphs
            if 'paragraphs' in sections:
                paragraphs = content.find_all('p')
                content_parts.extend([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        # Combine all content
        results['content'] = '\n'.join(filter(None, content_parts))

        # Extract contact information from main page
        results['contact_info']['emails'].extend(self.extract_emails(str(main_soup)))
        results['contact_info']['phones'].extend(self.extract_phones(str(main_soup)))

        # If no contact info found, try contact page
        if not results['contact_info']['emails'] and not results['contact_info']['phones']:
            contact_url = self.find_contact_page(main_soup, base_url)
            if contact_url:
                contact_soup = self.get_page_content(contact_url, driver)
                if contact_soup:
                    results['contact_info']['emails'].extend(self.extract_emails(str(contact_soup)))
                    results['contact_info']['phones'].extend(self.extract_phones(str(contact_soup)))

        # Extract social media links
        results['social_links'] = self.extract_social_links(main_soup, base_url)

        # Extract metadata
        results['metadata'] = {
            'title': main_soup.title.string if main_soup.title else None,
            'meta_description': main_soup.find('meta', {'name': 'description'})['content'] if main_soup.find('meta', {'name': 'description'}) else None,
            'meta_keywords': main_soup.find('meta', {'name': 'keywords'})['content'] if main_soup.find('meta', {'name': 'keywords'}) else None
        }

        # Remove duplicates and clean up data
        results['contact_info']['emails'] = list(set(results['contact_info']['emails']))
        results['contact_info']['phones'] = list(set(results['contact_info']['phones']))

        return results

def scrape_website(url: str, driver, sections: List[str] = None) -> Dict[str, any]:
    """Wrapper function for backward compatibility."""
    scraper = AdvancedScraper()
    return scraper.scrape_website(url, driver, sections)
