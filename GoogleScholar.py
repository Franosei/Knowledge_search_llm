import os
from typing import List, Dict
from scholarly import scholarly

def search_articles(keyword: str, max_articles: int = 10) -> List[Dict]:
    search_query = scholarly.search_pubs(keyword)
    articles = []

    for _ in range(max_articles * 2):  # Fetch more than needed to ensure we have enough to filter
        try:
            article = next(search_query)
            if 'pub_year' in article['bib']:  # Ensure the publication year is present
                articles.append(article)
        except StopIteration:
            break
    
    # Sort articles by publication year (newest first)
    articles.sort(key=lambda x: x['bib']['pub_year'], reverse=True)

    # Return the top max_articles articles
    return articles[:max_articles]

def extract_important_sections(article) -> Dict[str, str]:
    sections = {
        'Title': article['bib']['title'],
        'Key points': '',
        'Abstract': article['bib'].get('abstract', ''),
        'Introduction': '',
        'Results': '',
        'Discussion': '',
        'Methods': '',
        'Conclusion': '',
        'Data availability': ''
    }

    # Since we're using scholarly, we only have limited information directly available.
    # Further scraping or fetching the full text is needed for detailed sections.
    return sections

def save_sections_to_file(sections: Dict[str, str], filename: str):
    with open(filename, 'w', encoding='utf-8') as file:
        for section, content in sections.items():
            file.write(f"{section}\n{'='*len(section)}\n{content}\n\n")

def main_google(keyword: str, max_articles: int = 10) -> str:
    articles = search_articles(keyword, max_articles)
    os.makedirs('articles', exist_ok=True)
    
    messages = []
    for i, article in enumerate(articles):
        sections = extract_important_sections(article)

        filename = f"articles/article_{i+1}.txt"
        save_sections_to_file(sections, filename)
        pub_url = article['pub_url'] if 'pub_url' in article else "No URL available"
        message = f"{i+1}. {pub_url}"
        messages.append(message)
    
    return "\n".join(messages)
