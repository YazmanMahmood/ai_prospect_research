from transformers import pipeline

# Initialize Hugging Face summarization pipeline
try:
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    print("Summarizer model loaded successfully.")
except Exception as e:
    print(f"Error loading summarizer model: {str(e)}")
    summarizer = None

def summarize_text(text_data):
    """Summarizes the given text data using the Hugging Face summarization model."""
    
    # If summarizer model is not available or the text is empty, return a default message
    if not text_data or not summarizer:
        return "No content to summarize or summarizer model not available."
    
    try:
        # If the content is too short, return a message instead of summarizing
        if len(text_data.split()) < 20:
            return "Content is too short to summarize effectively."
        
        # Perform the summarization
        summary = summarizer(text_data, max_length=130, min_length=30, do_sample=False)
        
        # Check if the summarization output is in the expected format
        if summary and isinstance(summary, list) and len(summary) > 0 and "summary_text" in summary[0]:
            return summary[0]['summary_text']
        else:
            return "Summarization returned an unexpected format."
    
    except IndexError as e:
        print(f"Error in summarization: index out of range - {str(e)}")
        return "Error in summarization: content might be too short or unstructured."
    
    except Exception as e:
        print(f"Error in summarization: {str(e)}")
        return f"Error in summarization: {str(e)}"

# Example usage for testing purposes
if __name__ == '__main__':
    test_text = """Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term "artificial intelligence" is often used to describe machines (or computers) that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem-solving"."""
    
    print(summarize_text(test_text))
