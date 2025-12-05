from utils.sitemaps import get_sitemap_urls
from docling.document_converter import DocumentConverter
from utils.clean_docs import extract_clean_text_generic
converter = DocumentConverter()

sitemap_urls = get_sitemap_urls("https://aws.amazon.com/bedrock/")
conv_results_iter = converter.convert_all(sitemap_urls)

docs = []
for result in conv_results_iter:
    if result.document:
        cleaned = extract_clean_text_generic(result.document)
        docs.append("\n".join(cleaned))
        
        
print(docs)