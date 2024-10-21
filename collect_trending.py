import requests
from bs4 import BeautifulSoup
import json
import os
import hashlib
import time
import argparse
from urllib.parse import urljoin


CACHE_DIR = "cache"

def makecachedir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def cache_get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    hash_url = hashlib.md5(url.encode()).hexdigest()
    cache_path = os.path.join(CACHE_DIR, hash_url)

    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return f.read()

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(cache_path, 'w') as f:
            f.write(response.text)
        return response.text
    else:
        raise Exception(f"Failed to retrieve URL: {url}")



def get_trending_article_links():
    url = "https://montrealgazette.com/category/news/"
    html = cache_get(url)
    soup = BeautifulSoup(html, 'html.parser')

    article_elements = soup.find_all('a', class_='article-card__link')
    
    links = [urljoin(url, article['href']) for article in article_elements]
    
    return links

def scrape_article(url):
    html = cache_get(url)
    soup = BeautifulSoup(html, 'html.parser')

    


    title = soup.find('h1', class_='article-title').get_text(strip=True) if soup.find('h1', class_='article-title') else 'No title found'
    date = soup.find('span', class_='published-date__since').get('datetime') if soup.find('span', class_='published-date__since') else 'No date found'
    author = soup.find('span', class_='published-by__author').get_text(strip=True) if soup.find('span', class_='published-by__author') else 'No author found'
    blurb = soup.find('p', class_='article-subtitle').get_text(strip=True) if soup.find('p', class_='article-subtitle') else 'No blurb found'

    

    return {
        'title': title,
        'publication_date': date,
        'author': author,
        'blurb': blurb
    }



def collect_trending_articles(output_file):
    trend_links = get_trending_article_links()
    trend_articles = []

    for link in trend_links[:5]: 
        
            article_data = scrape_article(link)
            trend_articles.append(article_data)
        

    with open(output_file, 'w') as f:
        json.dump(trend_articles, f, indent=4)
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    makecachedir()

    parser = argparse.ArgumentParser(description="Scrape articles")
    parser.add_argument('-o', '--output', required=True)
    args = parser.parse_args()



    collect_trending_articles(args.output)
