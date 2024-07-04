import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to get the review data
def get_review_data(soup, product_id):
    reviews = []
    for review in soup.find_all('div', {'data-hook': 'review'}):
        review_text = review.find('span', {'data-hook': 'review-body'}).text.strip()
        helpful_votes = review.find('span', {'data-hook': 'helpful-vote-statement'})
        helpful_votes = helpful_votes.text.strip() if helpful_votes else '0'
        review_date = review.find('span', {'data-hook': 'review-date'}).text.strip()
        reviewer = review.find('span', {'class': 'a-profile-name'}).text.strip()
        vine_voice = review.find('span', {'data-hook': 'vine-review'})
        vine_voice = bool(vine_voice)
        verified_purchase = review.find('span', {'data-hook': 'avp-badge'})
        verified_purchase = bool(verified_purchase)

        reviews.append({
            'product_identifier': product_id,
            'review_text': review_text,
            'no_helpful_votes': helpful_votes,
            'review_date': review_date,
            'reviewer': reviewer,
            'vine_voice': vine_voice,
            'verified_purchase': verified_purchase
        })
    return reviews

# Function to get product URLs from the search results page
def get_product_urls(search_url):
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    product_urls = []
    for product in soup.find_all('div', {'data-component-type': 's-search-result'}):
        link = product.find('a', {'class': 'a-link-normal s-no-outline'})
        if link:
            product_urls.append('https://www.amazon.com' + link['href'])
    return product_urls

# URL of the search results page
search_url = "https://www.amazon.com/s?i=computers&rh=n:565108,p_36:2421886011&s=exact-aware-popularity-rank&ds=v1:FQy9V088cXQ56+NygtPl5/hTz8psCEVCk5t9EzMs820&content-id=amzn1.sym.4d915fa8-ca05-4073-b385-a93e1e1dd22d&qid=1685043013"

# Get product URLs from the search results page
product_urls = get_product_urls(search_url)

# Store all reviews
all_reviews = []

for product_url in product_urls:
    product_id = product_url.split('/')[-1]  # Extract product identifier from URL
    for page in range(1, 9):  # Loop through the first 8 pages of reviews
        review_url = f"{product_url}/ref=cm_cr_getr_d_paging_btm_{page}?pageNumber={page}"
        response = requests.get(review_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        reviews = get_review_data(soup, product_id)
        all_reviews.extend(reviews)
        time.sleep(2)  # Be polite and don't overwhelm the server with requests

# Create a DataFrame
df = pd.DataFrame(all_reviews)

# Save to an Excel file
df.to_excel('reviews.xlsx', index=False)
print("Reviews have been saved to reviews.xlsx")
