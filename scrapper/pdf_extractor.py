import requests

def extract_pdf_links(soup, base_url):
    from urllib.parse import urljoin
    pdf_links = []
    for link_tag in soup.find_all('a', href=True):
        href = link_tag['href']
        if href.endswith('.pdf'):
            # Convert relative URL to absolute
            pdf_url = urljoin(base_url, href)
            pdf_links.append(pdf_url)
    return pdf_links

def extract_pdf_text(pdf_url):
    """
    Extracts text from a PDF located at the specified URL.
    
    Args:
        pdf_url (str): The URL of the PDF file.
        
    Returns:
        str: The extracted text from the PDF.
    """
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        # You'd typically use a PDF parsing library here, such as PyMuPDF or pdfplumber
        pdf_text = "Simulated extracted text"  # Placeholder for extracted text
        return pdf_text

    except requests.RequestException as e:
        print(f"Failed to retrieve PDF: {e}")
        return "Could not retrieve PDF content."
