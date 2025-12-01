from document_summarizer import summarize_document

# Audio file to summarize
file_path = "/home/tanzir/Downloads/Bioinformatics_LLM_QuickGuide.docx"

print("Starting summarization...")
print(f"File: {file_path}")
print("-" * 60)

result = summarize_document(file_path)

print("\n SUMMARY:")
print("=" * 60)
print(result["summary"])
print("=" * 60)
print(f"\n File Name: {result['file_name']}")
print(f"File Size: {result['file_size']}")
print("\nDone!")
