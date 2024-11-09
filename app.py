from flask import Flask, render_template, request, jsonify
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Import custom modules
from gemini_helper import GeminiHelper
from scrapper.scraper import scrape_website
from scrapper.advanced_analysis import (
    extract_contact_info, extract_social_links, keyword_analysis, 
    categorize_industry, detect_key_personnel
)
from scrapper.pdf_extractor import extract_pdf_links, extract_pdf_text
from scrapper.competitor_analysis import CompetitorAnalysis
from scrapper.traffic_analysis import TrafficAnalysis

# Initialize Flask app
app = Flask(__name__)

# Initialize Gemini API helpers with the API key
GEMINI_API_KEY = "AIzaSyAkp7pe-jtShZCbAM9UcNnfU_Dyix4ocBw"
gemini_helper = GeminiHelper(GEMINI_API_KEY)
competitor_analysis = CompetitorAnalysis(GEMINI_API_KEY)
traffic_analysis = TrafficAnalysis(GEMINI_API_KEY)


def get_selenium_driver():
    """Set up and return a Selenium WebDriver instance with increased timeouts."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-javascript")  # Try without JavaScript first
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Increase timeouts
    driver.set_page_load_timeout(60)  # Increase to 60 seconds
    driver.set_script_timeout(60)
    driver.implicitly_wait(20)
    
    return driver

@app.route('/')
def home():
    """Render the main HTML template."""
    return render_template('index.html')
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')
    sections = data.get('sections', ['title', 'headings', 'paragraphs'])

    if not url:
        return jsonify({"error": "No URL provided."}), 400

    driver = None
    try:
        # First try without JavaScript
        driver = get_selenium_driver()
        try:
            driver.get(url)
            time.sleep(10)  # Increased wait time
        except Exception as e:
            # If failed, retry with JavaScript enabled
            driver.quit()
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.set_page_load_timeout(60)
            driver.get(url)
            time.sleep(10)

        # Scrape the website content with the driver
        print("Starting to scrape the website...")
        try:
            scraped_data = scrape_website(url, driver, sections)
            if not scraped_data:
                return jsonify({"error": "Failed to scrape website content."}), 500
        except Exception as e:
            # Try alternative content extraction if regular scraping fails
            alternative_content = extract_alternative_content(driver)
            if alternative_content:
                scraped_data = {
                    'content': alternative_content,
                    'soup': BeautifulSoup(driver.page_source, 'html.parser')
                }
            else:
                return jsonify({"error": f"Failed to scrape website: {str(e)}"}), 500

        content = scraped_data.get('content', "")
        soup = scraped_data.get('soup')

        if not soup:
            return jsonify({"error": "Failed to parse HTML content."}), 500

        # Generate website summary with improved error handling
        try:
            summary = gemini_helper.generate_website_summary(content)
            if not summary or "XYZ Corporation" in summary:
                alternative_content = extract_alternative_content(driver)
                summary = gemini_helper.generate_website_summary(alternative_content) or "Unable to generate summary at this time."
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            summary = "Unable to generate summary at this time."

        # Advanced analyses
        contact_info = extract_contact_info(content)
        social_links = extract_social_links(soup)
        keywords = keyword_analysis(content)
        industry_category = categorize_industry(content)
        key_personnel = detect_key_personnel(content)

        # Set base_url for handling relative links in PDFs
        base_url = url

        # Extract PDF information
        pdf_links = extract_pdf_links(soup, base_url)
        pdf_texts = {link: extract_pdf_text(link) for link in pdf_links}

        # Add traffic analysis
        traffic_data = traffic_analysis.generate_traffic_analysis(content)

        # Close the Selenium driver
        driver.quit()

        # Return JSON response with the analyzed data
        return jsonify({
            "summary": summary,
            "contact_info": contact_info,
            "social_links": social_links,
            "keywords": keywords,
            "industry_category": industry_category,
            "key_personnel": key_personnel,
            "pdf_texts": pdf_texts,
            "traffic_data": traffic_data
        })

    except Exception as e:
        print("An error occurred during scraping or processing:", str(e))
        return jsonify({"error": f"Internal server error occurred: {str(e)}"}), 500
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def extract_alternative_content(driver):
    """Extract content using multiple fallback methods"""
    try:
        # Method 1: Get text using JavaScript
        js_text = driver.execute_script("""
            return Array.from(document.body.getElementsByTagName('*'))
                .filter(element => {
                    const style = window.getComputedStyle(element);
                    return style.display !== 'none' && 
                           style.visibility !== 'hidden' && 
                           element.offsetWidth > 0 && 
                           element.offsetHeight > 0;
                })
                .map(element => element.textContent.trim())
                .filter(text => text.length > 50)
                .join('\\n');
        """)
        
        if js_text and len(js_text) > 500:
            return js_text
            
        # Method 2: Get text from main content areas
        main_content = driver.find_elements_by_css_selector('main, article, .content, #content, .main')
        if main_content:
            content = '\n'.join([elem.text for elem in main_content if elem.text])
            if content and len(content) > 500:
                return content
                
        # Method 3: Get all visible text
        body_text = driver.find_element_by_tag_name('body').text
        if body_text and len(body_text) > 500:
            return body_text
            
        return None
        
    except Exception as e:
        print(f"Error extracting alternative content: {str(e)}")
        return None

@app.route('/analyze_competitors', methods=['POST'])
def analyze_competitors():
    """Analyze competitors for a given target company and industry."""
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided for competitor analysis."}), 400

    driver = None
    try:
        # Set up WebDriver and load the URL
        driver = get_selenium_driver()
        driver.get(url)
        time.sleep(2)  # Wait for page to load

        # Scrape the website content
        scraped_data = scrape_website(url, driver, ['title', 'headings', 'paragraphs'])
        website_content = scraped_data.get('content', "")
        
        if not website_content:
            return jsonify({"error": "Failed to scrape content for competitor analysis."}), 500

        # Generate competitor analysis using Gemini
        competitor_summary = competitor_analysis.generate_competitor_analysis(website_content)

        if competitor_summary:
            return jsonify({
                "status": "success",
                "competitor_analysis": competitor_summary
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Unable to generate competitor analysis at this time."
            }), 500

    except Exception as e:
        print("An error occurred during competitor analysis:", str(e))
        return jsonify({"error": f"Internal server error occurred: {str(e)}"}), 500
    finally:
        if driver:
            driver.quit()

# Move app.run() outside of the route function
if __name__ == '__main__':
    app.run(debug=True)
