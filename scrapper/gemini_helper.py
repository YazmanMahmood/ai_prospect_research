import google.generativeai as genai
from typing import Optional
import re

class GeminiHelper:
    def __init__(self, api_key: str, model_name: str = 'gemini-pro'):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def clean_text(self, text: str) -> str:
        """Clean text by removing markdown, quotes, and extra whitespace."""
        # Remove markdown stars and other symbols
        text = re.sub(r'[\*\#\_\~\`\"]', '', text)
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Remove leading/trailing whitespace from each line
        text = '\n'.join(line.strip() for line in text.split('\n'))
        return text.strip()

    def generate_website_summary(self, website_content: str) -> Optional[str]:
        """Generate a comprehensive website summary using Gemini."""
        try:
            prompt = f"""
            Create a clear and structured company overview based on the following website content.
            Format your response exactly as shown below, with no markdown or special characters:

            COMPANY OVERVIEW
            [Write 2-3 sentences about the company's main business and purpose]

            MAIN OFFERINGS
            1. [First main product/service with brief description]
            2. [Second main product/service with brief description]
            3. [Third main product/service with brief description]

            CORE STRENGTHS
            1. [First key strength with explanation]
            2. [Second key strength with explanation]
            3. [Third key strength with explanation]

            MARKET POSITION
            [2-3 sentences about the company's position in their industry]

            Website Content:
            {website_content[:4000]}
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Clean the response text
                cleaned_response = self.clean_text(response.text)
                
                # Format the sections consistently
                sections = cleaned_response.split('\n\n')
                formatted_sections = []
                
                for section in sections:
                    if ':' not in section and section.isupper():
                        # It's a header
                        formatted_sections.append(f"{section}")
                    else:
                        # It's content
                        formatted_sections.append(section)
                
                return '\n\n'.join(formatted_sections)
            
            return None

        except Exception as e:
            print(f"Error generating summary with Gemini: {str(e)}")
            return None
