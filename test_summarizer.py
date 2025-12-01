from document_summarizer import summarize_document, summarize_text
import time

print("=" * 70)
print("DOCUMENT SUMMARIZER - Using OpenAI File Upload")
print("=" * 70)
print()

# Example 1: Summarize plain text
print("Example 1: Summarize Text Directly")
print("-" * 70)
sample_text = """
Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to 
the natural intelligence displayed by humans and animals. Leading AI textbooks define 
the field as the study of "intelligent agents": any device that perceives its environment 
and takes actions that maximize its chance of successfully achieving its goals. 
Colloquially, the term "artificial intelligence" is often used to describe machines 
that mimic "cognitive" functions that humans associate with the human mind, such as 
"learning" and "problem solving". As machines become increasingly capable, tasks 
considered to require "intelligence" are often removed from the definition of AI, 
a phenomenon known as the AI effect. A quip in Tesler's Theorem says "AI is whatever 
hasn't been done yet." For instance, optical character recognition is frequently 
excluded from things considered to be AI, having become a routine technology.
Modern machine learning is the dominant approach to AI today. Deep learning, a subset
of machine learning using artificial neural networks, has driven recent advances in
image recognition, natural language processing, and game playing.
"""

result = summarize_text(sample_text, max_length=80)
print(f"Original Length: {result['original_length']} words")
print(f"Summary Length: {result['summary_length']} words")
print(f"\nSummary:\n{result['summary']}")
print()
print()

# Example 2: Create and summarize a text file
print("Example 2: Summarize Text File (uploaded to OpenAI)")
print("-" * 70)

# Create a sample text file
with open('/tmp/climate_article.txt', 'w') as f:
    f.write("""
Climate Change: A Global Challenge

Climate change is one of the most pressing challenges facing humanity today. 
The Earth's average temperature has risen by about 1.1°C since the late 19th century, 
primarily due to human activities like burning fossil fuels, deforestation, and 
industrial processes. This warming has led to melting ice caps, rising sea levels, 
more frequent extreme weather events, and disruptions to ecosystems worldwide.

The Science Behind It
Scientists agree that we must limit global warming to 1.5°C above pre-industrial 
levels to avoid the most catastrophic impacts. The greenhouse effect, while natural 
and necessary for life, has been amplified by human emissions of carbon dioxide, 
methane, and other greenhouse gases. These gases trap heat in the atmosphere, 
leading to a warming planet.

Solutions and Actions
This requires immediate and substantial reductions in greenhouse gas emissions. 
Renewable energy sources like solar and wind power, along with energy efficiency 
improvements, are key solutions. Additionally, protecting and restoring forests, 
which absorb carbon dioxide, is crucial. Electric vehicles, sustainable agriculture,
and green building practices all contribute to mitigation efforts.

Individual Responsibility
Individual actions also matter. Reducing energy consumption, choosing sustainable 
transportation, eating less meat, and supporting climate-friendly policies can all 
contribute to addressing this global crisis. The challenge is significant, but with 
collective action from governments, businesses, and individuals, we can work towards 
a more sustainable future for generations to come.
""")

print("Uploading file to OpenAI and generating summary...")
print("(This may take 10-20 seconds)")
result = summarize_document('/tmp/climate_article.txt', max_length=100)
print(f"\nDocument Type: {result['document_type']}")
print(f"File Name: {result['file_name']}")
print(f"File Size: {result['original_size']}")
print(f"\nSummary:\n{result['summary']}")
print()
print()

print("=" * 70)
print("SUPPORTED FILE TYPES:")
print("=" * 70)
print("""
TEXT FILES (uploaded to OpenAI):
- .txt, .md, .pdf, .docx, .csv, .json, .xml, .html, .py, .js

AUDIO FILES (transcribed via Whisper):
- .mp3, .wav, .m4a, .mp4, .mpeg, .mpga, .webm

IMAGE FILES (analyzed via Vision API):
- .png, .jpg, .jpeg, .gif, .webp

EXAMPLES:

# Summarize PDF
result = summarize_document('research_paper.pdf', max_length=200)

# Summarize audio
result = summarize_document('podcast_episode.mp3', max_length=150)

# Summarize image
result = summarize_document('infographic.png')

# Summarize with custom prompt
result = summarize_document(
    'meeting_notes.txt',
    custom_prompt="Extract all action items and decisions from this document."
)
""")

