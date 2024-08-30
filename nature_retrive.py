import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import os

def search_articles(keyword: str, max_articles: int = 10) -> List[str]:
    search_url = f"https://www.nature.com/search?q={keyword.replace(' ', '%20')}"
    response = requests.get(search_url)
    if response.status_code != 200:
        raise Exception("Failed to retrieve search results.")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    article_links = []

    for article in articles:
        link = article.find('a', href=True)
        date_tag = article.find('time')
        if link and date_tag:
            article_url = "https://www.nature.com" + link['href']
            publication_date = date_tag['datetime']
            article_links.append((article_url, publication_date))
    
    # Sort articles by publication date (newest first)
    article_links.sort(key=lambda x: datetime.strptime(x[1], '%Y-%m-%d'), reverse=True)

    # Return the top max_articles links
    return [link for link, _ in article_links[:max_articles]]

def extract_important_sections(article_url: str) -> Dict[str, str]:
    response = requests.get(article_url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve article page: {article_url}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    sections = {
        'Title': '',
        'Key points': "",
        'Abstract': '',
        'Introduction': '',
        'Results': '',
        'Discussion': '',
        'Methods': '',
        'Conclusion': '',
        'Data availability': ''
    }
    
    # Extract Title
    title_tag = soup.find('title')
    if title_tag:
        sections['Title'] = title_tag.get_text().strip()

    # Extract Abstract
    abstract_tag = soup.find('div', class_='c-article-section__content')
    if abstract_tag:
        sections['Abstract'] = abstract_tag.get_text(separator="\n").strip()

    # Extract other sections
    section_names = ['Introduction','Key points', 'Results', 'Discussion', 'Methods', 'Conclusion', 'Data availability']

    for section_name in section_names:
        section_tag = soup.find(lambda tag: tag.name == "h2" and section_name.lower() in tag.get_text().lower())
        if section_tag:
            section_content = []
            for sibling in section_tag.find_next_siblings():
                if sibling.name == "h2":
                    break
                section_content.append(sibling.get_text(separator="\n").strip())
            sections[section_name] = "\n".join(section_content)
    
    return sections

def save_sections_to_file(sections: Dict[str, str], filename: str):
    with open(filename, 'w', encoding='utf-8') as file:
        for section, content in sections.items():
            file.write(f"{section}\n{'='*len(section)}\n{content}\n\n")

def main(keyword: str, max_articles: int = 10) -> str:
    articles = search_articles(keyword, max_articles)
    os.makedirs('articles', exist_ok=True)
    
    messages = []
    for i, article_url in enumerate(articles):
        sections = extract_important_sections(article_url)

        filename = f"articles/article_{i+1}.txt"
        name = f"article_{i+1}"
        save_sections_to_file(sections, filename)
        message = f"{i+1}.{article_url}"
        #print(message)  # Optional: keep this if you also want to print the message
        messages.append(message)
    
    return "\n".join(messages)