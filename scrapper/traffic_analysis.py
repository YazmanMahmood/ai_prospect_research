import google.generativeai as genai
from typing import Optional

class TrafficAnalysis:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_traffic_analysis(self, website_content: str) -> Optional[str]:
        """
        Generate traffic statistics for the website.
        
        Args:
            website_content (str): The scraped content from the website
            
        Returns:
            str: Traffic statistics or None if generation fails
        """
        try:
            prompt = f"""
            just give me rough estimate. on website content
Only provide these 3 metrics with numbers, no additional text or explanation.
 Monthly Visits: X
 Average Time on Site: X minutes
 Bounce Rate: X%
 
write Please note that these are just estimates and the actual numbers may vary. in case you dont have knowledge and no other comment from your side

            Website content:
            {website_content[:4000]}
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            
            return None
            
        except Exception as e:
            print(f"Error generating traffic analysis with Gemini: {str(e)}")
            return None 