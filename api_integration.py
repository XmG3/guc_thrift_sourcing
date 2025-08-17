import requests
import base64
import json
from api_config import APP_ID, CERT_ID, DEV_ID, OAUTH_TOKEN

class EbayAPI:
    def __init__(self):
        self.app_id = APP_ID
        self.cert_id = CERT_ID
        self.dev_id = DEV_ID
        self.oauth_token = OAUTH_TOKEN
    
        self.base_url = "https://api.ebay.com"
    
    def get_oauth(self):
        url = f"{self.base_url}/identity/v1/oauth2/token"
    
        #basic auth header
        credentials = f"{self.app_id}:{self.cert_id}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {encoded_credentials}'
        }

        data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            token_data = response.json()
            self.oauth_token = token_data['access_token']
            return self.oauth_token
        else:
            raise Exception(f"Failed to get OAuth token: {response.status_code} - {response.text}")
    
    def search_items(self, query, category_id = None, max_results = 200, marketplace = 'EBAY_DE'):
        if not self.oauth_token:
            self.get_oauth()
        
        url = f"{self.base_url}/buy/browse/v1/item_summary/search"

        headers = {
            'Authorization': f'Bearer {self.oauth_token}',
            'Content-Type': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': marketplace
        }

        params = {
            'q': query,
            'limit': min(max_results, 200)
        }

        if category_id:
            params['category_ids'] = category_id

        response = requests.get(url, headers=headers, params = params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to search items: {response.status_code} - {response.text}")
    
    def get_details(self, item_id): 
        if not self.oauth_token:
            self.get_oauth_token()
            
        url = f"{self.base_url}/buy/browse/v1/item/{item_id}"
        
        headers = {
            'Authorization': f'Bearer {self.oauth_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Item details failed: {response.status_code} - {response.text}")
        
    def extract_item_data(self, api_item, known_brands):
        try:
            title = api_item.get('title', '')
            
            # Price extraction
            price_info = api_item.get('price', {})
            price = float(price_info.get('value', 0)) if price_info else 0
            
            # Condition mapping from eBay API to your system
            condition = api_item.get('condition', '')
            condition_map = {
                'NEW': 'Hervorragend',
                'NEW_OTHER': 'Hervorragend',
                'NEW_WITH_DEFECTS': 'Gut',
                'MANUFACTURER_REFURBISHED': 'Gut',
                'SELLER_REFURBISHED': 'Gut',
                'USED_EXCELLENT': 'Hervorragend',
                'USED_VERY_GOOD': 'Gut',
                'USED_GOOD': 'Gut',
                'USED_ACCEPTABLE': 'Akzeptabel',
                'FOR_PARTS_OR_NOT_WORKING': 'Defekt'
            }
            mapped_condition = condition_map.get(condition, condition)
            
            # Seller info
            seller_info = api_item.get('seller', {})
            # eBay returns percentage, convert to 5-point scale
            feedback_percentage = float(seller_info.get('feedbackPercentage', 0))
            seller_score = feedback_percentage / 20.0  # Convert 0-100% to 0-5 scale
            
            # Brand detection from title
            brand = api_item.get('brand', '')
            title_words = title.lower().split()
            for word in title_words:
                if word in known_brands:
                    brand = word
                    break
            
            # Vintage detection
            vintage_status = 'vintage' if 'vintage' in title.lower() or 'retro' in title.lower() else None
            
            return {
                'title': title,
                'price': price,
                'condition': mapped_condition,
                'seller_score': seller_score,
                'brand': brand,
                'vintage_status': vintage_status,
                'url': api_item.get('itemWebUrl', ''),
                'item_id': api_item.get('itemId', ''),
                'image_url': api_item.get('image', {}).get('imageUrl', ''),
                'location': api_item.get('itemLocation', {}).get('country', '')
            }
        except Exception as e:
            print(f"Error extracting item data: {e}")
            return None