import google.generativeai as genai
from typing import Optional

class CompetitorAnalysis:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        
        # Initialize the model correctly
        # Adjust this initialization according to the library's documentation
        self.model = genai.GenerativeModel('gemini-pro')  # Adjust as needed based on actual usage

    def generate_competitor_analysis(self, website_content: str) -> Optional[str]:
        """
        Generate a competitor analysis based on website content.
        """
        try:
            prompt = f"""
            Give me a very short 1-5 competitors on given website and
            
            provide a structured competitor analysis.
            Format exactly like this example, without any stars or markdown:

            TOP COMPETITORS:
            1. PepsiCo - Global beverage company with diverse portfolio
            2. Company Name - One line description
            3. Company Name - One line description
            4. Company Name - One line description
            5. Company Name - One line description

            Website content to analyze:
            {website_content[:4000]}
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Remove any markdown stars that might be in the response
                cleaned_response = response.text.replace('*', '').strip()
                return cleaned_response
            
            return None
        
        except Exception as e:
            print(f"Error generating competitor analysis with Gemini: {str(e)}")
            return None
