import re
from collections import Counter
from bs4 import BeautifulSoup
from transformers import pipeline
import requests
import spacy
from typing import Dict, List

# Load Hugging Face models
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    revision="714eb0f"
)

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
    revision="a4f8f3e"
)

# Load spaCy model for named entity recognition
nlp = spacy.load("en_core_web_sm")

def extract_contact_info(text: str) -> Dict[str, List[str]]:
    """
    Extract email addresses and phone numbers from the given text.
    
    Args:
    - text (str): The text to extract contact information from.
    
    Returns:
    - dict: A dictionary with keys 'emails' and 'phones', containing lists of extracted email addresses and phone numbers.
    """
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    return {"emails": emails, "phones": phones}

def extract_social_links(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extracts social media links from the page, including icons and labels, and checks meta tags and footers.
    
    Args:
    - soup (BeautifulSoup): Parsed HTML of the webpage.
    
    Returns:
    - dict: A dictionary with social media platform names as keys and URLs as values.
    """
    social_links = {}
    
    social_patterns = {
        'Facebook': r'(facebook|fb)\.com',
        'Twitter': r'twitter\.com',
        'LinkedIn': r'linkedin\.com',
        'Instagram': r'instagram\.com',
        'YouTube': r'youtube\.com'
    }
    
    # 1. Look for links with common social media patterns in href or text/aria-label attributes
    for tag in soup.find_all('a', href=True):
        href = tag.get('href', '').lower()
        text = (tag.get_text() or '').lower()
        aria_label = (tag.get('aria-label') or '').lower()
        
        for platform, pattern in social_patterns.items():
            if re.search(pattern, href) or re.search(pattern, text) or re.search(pattern, aria_label):
                social_links[platform] = href
                break  # Stop once a link is found for the current platform

    # 2. Check meta tags for social media links (commonly in og:url)
    if not social_links:
        for meta in soup.find_all('meta', property=True, content=True):
            property = meta.get('property', '').lower()
            content = meta['content'].lower()
            if 'og:' in property:
                for platform, pattern in social_patterns.items():
                    if re.search(pattern, content):
                        social_links[platform] = content
                        break  # Stop once a link is found for the current platform

    # 3. Look in the footer if no social links were found in main tags
    if not social_links:
        footer = soup.find('footer')
        if footer:
            for tag in footer.find_all('a', href=True):
                href = tag.get('href', '').lower()
                for platform, pattern in social_patterns.items():
                    if re.search(pattern, href):
                        social_links[platform] = href
                        break  # Stop once a link is found for the current platform

    return social_links

def keyword_analysis(text: str) -> List[Dict[str, str]]:
    """
    Perform keyword analysis on the given text and return the top 10 most common keywords.
    
    Args:
    - text (str): The text to analyze.
    
    Returns:
    - list: A list of dictionaries, where each dictionary has keys 'keyword' and 'count'.
    """
    words = re.findall(r'\w+', text.lower())
    common_words = Counter(words).most_common(10)
    return [{"keyword": word, "count": count} for word, count in common_words]

def perform_sentiment_analysis(text: str) -> Dict[str, float]:
    """
    Perform sentiment analysis on the given text and return the sentiment label and score.
    
    Args:
    - text (str): The text to analyze.
    
    Returns:
    - dict: A dictionary with keys 'label' and 'score', containing the sentiment label and score.
    """
    sentiments = sentiment_analyzer(text[:500])  # Limit length for performance
    return sentiments[0] if sentiments else {"label": "neutral", "score": 0}

def categorize_industry(text: str) -> str:
    """
    Categorize the given text into an industry based on the presence of industry-specific keywords.
    
    Args:
    - text (str): The text to analyze.
    
    Returns:
    - str: The industry category that best matches the text.
    """
    industry_keywords = {
        "Technology": ["software", "AI", "tech", "computer", "cloud", "IT", "digital"],
        "Healthcare": ["health", "medicine", "hospital", "patient", "medical", "pharma"],
        "Finance": ["bank", "financial", "investment", "money", "loan", "insurance"],
        "Education": ["education", "university", "school", "student", "learning", "academy","courses","guides"],
        "Entertainment": ["entertainment", "movie", "music", "film", "game", "media"],
        "Retail": ["shopping", "store", "ecommerce", "marketplace", "fashion", "goods"],
        "Travel": ["tourism", "vacation", "hotel", "resort", "adventure", "trip"],
        "Real Estate": ["property", "homes", "apartments", "realty", "estate", "land"],
        "Food & Beverage": ["restaurant", "catering", "recipes", "meal", "cafe", "dining"],
        "Sports": ["fitness", "athletics", "team", "stadium", "competition", "game"],
        "Automotive": ["car", "vehicle", "automobile", "motor", "repair", "dealer"],
        "Non-Profit": ["charity", "donation", "volunteer", "foundation", "NGO", "cause"],
        "Art & Design": ["gallery", "art", "creative", "design", "craft", "illustration"],
        "Construction": ["building", "contractor", "architecture", "construction", "site", "project"],
        "Agriculture": ["farm", "agriculture", "crops", "livestock", "harvest", "greenhouse"]
    }
    
    category_scores = {category: sum(text.count(word) for word in words) 
                       for category, words in industry_keywords.items()}
    return max(category_scores, key=category_scores.get)

def detect_key_personnel(text: str) -> List[str]:
    """
    Detect the top 5 key personnel mentioned in the given text.
    
    Args:
    - text (str): The text to analyze.
    
    Returns:
    - list: A list of the top 5 key personnel names mentioned in the text.
    """
    doc = nlp(text)
    potential_names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
    unique_names = list(set(potential_names))
    return unique_names[:5]  # Limit to top 5 names