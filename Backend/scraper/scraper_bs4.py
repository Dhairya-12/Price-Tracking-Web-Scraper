import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin

class AmazonScraper:
    def __init__(self):
        self.base_url = "https://www.amazon.ca"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }

    def search(self, query):
        """Search for products on Amazon"""
        search_url = f"{self.base_url}/s?k={query.replace(' ', '+')}"
        
        # Add random delay to avoid getting blocked
        time.sleep(random.uniform(1, 3))
        
        try:
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            return self.parse_search_results(response.text)
        except requests.RequestException as e:
            print(f"Error searching Amazon: {e}")
            return []

    def parse_search_results(self, html):
        """Parse the search results page"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find all product containers
        product_divs = soup.select('div[data-component-type="s-search-result"]')
        
        for div in product_divs:
            try:
                # Extract product information
                name_elem = div.select_one('h2 a span')
                price_elem = div.select_one('span.a-offscreen')
                image_elem = div.select_one('img.s-image')
                url_elem = div.select_one('h2 a')
                
                if not all([name_elem, price_elem, image_elem, url_elem]):
                    continue
                
                name = name_elem.text.strip()
                price_text = price_elem.text.strip().replace('$', '').replace(',', '')
                try:
                    price = float(price_text)
                except ValueError:
                    continue
                
                image_url = image_elem.get('src', '')
                product_url = urljoin(self.base_url, url_elem.get('href', ''))
                
                products.append({
                    "name": name,
                    "price": price,
                    "img": image_url,
                    "url": product_url
                })
                
            except Exception as e:
                print(f"Error parsing product: {e}")
                continue
        
        return products

def save_results(results):
    """Save results to a JSON file"""
    data = {"results": results}
    with open("results.json", "w") as f:
        json.dump(data, f)

def post_results(results, endpoint, search_text, source):
    """Post results to the backend API"""
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "data": results,
        "search_text": search_text,
        "source": source
    }
    
    try:
        response = requests.post(
            f"http://localhost:5000{endpoint}",
            headers=headers,
            json=data
        )
        print(f"Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error posting results: {e}")

def main(search_text):
    """Main function to run the scraper"""
    scraper = AmazonScraper()
    results = scraper.search(search_text)
    
    if results:
        save_results(results)
        post_results(results, "/api/results", search_text, "amazon.ca")
    else:
        print("No results found")

if __name__ == "__main__":
    # Test the scraper
    main("ryzen 9 3950x") 