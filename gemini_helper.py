# gemini_helper.py
import google.generativeai as genai
from typing import Optional

class GeminiHelper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_website_summary(self, website_content: str) -> Optional[str]:
        """
        Generate a comprehensive website summary using Gemini.
        
        Args:
            website_content (str): The scraped content from the website
            
        Returns:
            str: A 200-500 word summary of the website
        """
        try:
            prompt = f"""
            Based on the following website content, create a professional and informative summary 
            between 200-500 words. Focus on key business aspects, offerings, and unique value propositions.
            Include relevant industry insights if apparent. Make it concise yet comprehensive.

            Website Content:
            {website_content}
            """
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                # Clean and format the response
                summary = response.text.strip()
                # Ensure the summary meets length requirements
                words = summary.split()
                if len(words) < 200:
                    # If too short, request more details
                    additional_prompt = f"""
                    Please expand the following summary to include more details, 
                    aiming for at least 200 words:
                    {summary}
                    """
                    response = self.model.generate_content(additional_prompt)
                    summary = response.text.strip()
                elif len(words) > 500:
                    # If too long, request condensing
                    condense_prompt = f"""
                    Please condense the following summary to a maximum of 500 words 
                    while maintaining all key information:
                    {summary}
                    """
                    response = self.model.generate_content(condense_prompt)
                    summary = response.text.strip()
                
                return summary
            
            return None
            
        except Exception as e:
            print(f"Error generating summary with Gemini: {str(e)}")
            return None