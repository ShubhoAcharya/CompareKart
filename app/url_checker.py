import json
import re


def check_and_update_url(url):
    """
    Checks if the URL is from Flipkart or Amazon and updates the Flipkart URL if necessary.

    :param url: str, the URL to check
    :return: str, updated URL if it is a Flipkart URL, otherwise the original URL
    """
    flipkart_pattern = r'https?://(www\.)?flipkart\.com/.*'
    amazon_pattern = r'https?://(www\.)?amazon\.in/.*'
    
    if re.match(flipkart_pattern, url):
        # Assuming that product_urls.json has the updated Flipkart URL
        with open('product_urls.json', 'r') as f:
            product_urls = json.load(f)
            product_urls['flipkart_link'] = url
            with open('product_urls.json', 'w') as f:
                json.dump(product_urls, f, indent=4)
        return url
    
    elif re.match(amazon_pattern, url):
        # Assuming that product_urls.json has the updated Amazon URL
        with open('product_urls.json', 'r') as f:
            product_urls = json.load(f)
            product_urls['amazon_link'] = url
            with open('product_urls.json', 'w') as f:
                json.dump(product_urls, f, indent=4)
        return url
    
    else:
        return None
    
