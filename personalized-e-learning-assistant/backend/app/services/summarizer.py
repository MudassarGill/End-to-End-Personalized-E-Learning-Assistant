# Generate summary from text
from transformers import pipeline


# Load summarization pipeline (uses a pre-trained model)
summarizer_pipeline = None


def get_summarizer():
    global summarizer_pipeline
    if summarizer_pipeline is None:
        summarizer_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")
    return summarizer_pipeline


def generate_summary(text: str, max_length: int = 150, min_length: int = 50) -> str:
    """Generate a concise summary of the input text."""
    summarizer = get_summarizer()

    # Handle long texts by chunking
    max_input_length = 1024
    if len(text) > max_input_length:
        text = text[:max_input_length]

    result = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return result[0]["summary_text"]
