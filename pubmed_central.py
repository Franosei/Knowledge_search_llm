import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import os
import xml.etree.ElementTree as ET

def search_articles(keyword: str, max_articles: int = 10) -> List[str]:
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term={keyword.replace(' ', '+')}&retmax={max_articles}&retmode=json&sort=date"
    response = requests.get(search_url)
    if response.status_code != 200:
        raise Exception("Failed to retrieve search results.")
    
    result = response.json()
    article_ids = result.get("esearchresult", {}).get("idlist", [])
    
    article_links = [f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{id}/" for id in article_ids]
    return article_links

def fetch_article_xml(pmc_id: str) -> ET.Element:
    fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc_id}&retmode=xml"
    response = requests.get(fetch_url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve article XML: PMC{pmc_id}")
    
    return ET.fromstring(response.content)

def extract_important_sections(article_xml: ET.Element) -> Dict[str, str]:
    sections = {
        'Title': '',
        'Abstract': '',
        'Introduction': '',
        'Results': '',
        'Discussion': '',
        'Methods': '',
        'Conclusion': ''
    }

    # Extract Title
    title_tag = article_xml.find('.//article-title')
    if title_tag is not None:
        sections['Title'] = title_tag.text.strip()
    
    # Extract Abstract
    abstract_tag = article_xml.find('.//abstract')
    if abstract_tag is not None:
        sections['Abstract'] = ' '.join(abstract_tag.itertext()).strip()
    
    # Extract other sections
    body = article_xml.find('.//body')
    if body is not None:
        for sec in body.findall('.//sec'):
            sec_title = sec.find('title')
            if sec_title is not None:
                section_name = sec_title.text.strip().lower()
                for key in sections.keys():
                    if key.lower() in section_name:
                        sections[key] = ' '.join(sec.itertext()).strip()
    
    return sections

def save_sections_to_file(sections: Dict[str, str], filename: str):
    with open(filename, 'w', encoding='utf-8') as file:
        for section, content in sections.items():
            file.write(f"{section}\n{'='*len(section)}\n{content}\n\n")

def main_pubmed_central(keyword: str, max_articles: int = 10) -> str:
    articles = search_articles(keyword, max_articles)
    os.makedirs('articles', exist_ok=True)
    
    messages = []
    for i, article_url in enumerate(articles):
        pmc_id = article_url.split('/')[-2].replace('PMC', '')
        try:
            article_xml = fetch_article_xml(pmc_id)
            sections = extract_important_sections(article_xml)
            filename = f"articles/article_{i+1}.txt"
            save_sections_to_file(sections, filename)
            message = f"{i+1}. {article_url}"
            messages.append(message)
        except Exception as e:
            print(e)
    
    return "\n".join(messages)
