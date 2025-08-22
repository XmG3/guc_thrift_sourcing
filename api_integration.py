import requests, os, base64, json, time, re
from deep_translator import GoogleTranslator
from api_config import APP_ID, CERT_ID, DEV_ID, OAUTH_TOKEN


class EbayAPI:
    def __init__(self):
        self.app_id = APP_ID
        self.cert_id = CERT_ID
        self.dev_id = DEV_ID
        self.oauth_token = OAUTH_TOKEN
    
        self.base_url = "https://api.ebay.com"

        script_dir = os.path.dirname(os.path.abspath(__file__))
        brands_path = os.path.join(script_dir, "brands.json")

        with open(brands_path, "r", encoding="utf-8") as f:
            self.brand_data = json.load(f)
            self.known_brands = set()
            for tier in self.brand_data.values():
                self.known_brands.update(brand.lower() for brand in tier['brands'])
        
        self.translator = GoogleTranslator()
        self.market_languages = {
            'EBAY_DE': 'de',
            'EBAY_AT': 'de',
            'EBAY_FR': 'fr',
            'EBAY_IT': 'it',
            'EBAY_US': 'en'
        }

    
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
        
    
    def search_items(self, query, category_id=None, max_results=200, marketplace='EBAY_DE'):
    # For backward compatibility, if only one marketplace specified
        if isinstance(marketplace, str):
            return self.search_single_market(query, category_id, max_results, marketplace)
        
        # Multi-marketplace search
        if isinstance(marketplace, list) and len(marketplace) == 5:
            return self.search_multi_market(query, category_id, max_results, marketplace)
        
        # Default fallback
        return self.search_single_market(query, category_id, max_results, 'EBAY_DE')
    

    def search_single_market(self, query, category_id = None, max_results = 200, marketplace = 'EBAY_DE'):
        if not self.oauth_token:
            self.get_oauth()

        all_items = []
        offset = 0
        limit_per_request = 200

        while len(all_items) < max_results:
            remaining = max_results - len(all_items)
            current_limit = min(limit_per_request, remaining)
            
            url = f"{self.base_url}/buy/browse/v1/item_summary/search"
            headers = {
                'Authorization': f'Bearer {self.oauth_token}',
                'Content-Type': 'application/json',
                'X-EBAY-C-MARKETPLACE-ID': marketplace
            }
            params = {
                'q': query,
                'limit': current_limit,
                'offset': offset
            }
            if category_id:
                params['category_ids'] = category_id

            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 429:
                time.sleep(60)
                continue
            elif response.status_code != 200:
                raise Exception(f"Failed to search items: {response.status_code} - {response.text}")
            
            data = response.json()
            if 'itemSummaries' not in data or not data['itemSummaries']:
                break
                
            all_items.extend(data['itemSummaries'])
            
            if len(data['itemSummaries']) < current_limit:
                break
                
            offset += current_limit
            
            if max_results > 200:
                time.sleep(0.1)
        
        return {'itemSummaries': all_items, 'total': len(all_items)}
    
    def search_multi_market(self, query, category_id, max_results, markets= ['EBAY_DE', 'EBAY_AT', 'EBAY_FR', 'EBAY_IT', 'EBAY_GB']):
        results_per_market = max_results // len(markets)
        all_items = []
        seen_ids = set()

        for market in markets:
            translated_query = self.translate_query(query, market)
            market_results = self.search_single_market(translated_query, category_id, results_per_market, market)
            for item in market_results['itemSummaries']:
                item_id = item.get('itemId')
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    all_items.append(item)
            print(f"Searched {market} for '{translated_query}' and found {len(market_results['itemSummaries'])} results.")
        
        return {'itemSummaries': all_items, 'total': len(all_items)}
    
    def get_details(self, item_id): 
        if not self.oauth_token:
            self.get_oauth()
            
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
        
    def extract_item_data(self, api_item):
        try:
            title = api_item.get('title', '')
            
            # Price extraction
            price_info = api_item.get('price', {})
            price = float(price_info.get('value', 0)) if price_info else 0
            
            # Condition mapping from eBay API to your system
            condition = api_item.get('condition', '')
            
            # Brand detection from title
            brand = api_item.get('brand', '')
            if not brand:
                brand = self.detect_brand(title)
            
            # Vintage detection
            vintage_status = 'vintage' if 'vintage' in title.lower() or 'retro' in title.lower() else None

            # auction or buy-it-now
            purchase_method = api_item.get('buyingOptions', [])

            
        
            return {
                'title': title,
                'price': price,
                'condition': condition,
                'brand': brand,
                'location': api_item.get('itemLocation', {}).get('country', 'Unknown'),
                'vintage_status': vintage_status,
                'url': api_item.get('itemWebUrl', ''),
                'item_id': api_item.get('itemId', ''),
                'image_url': api_item.get('image', {}).get('imageUrl', ''),
                'purchase_method': purchase_method
            }
        except Exception as e:
            print(f"Error extracting item data: {e}")
            return None
        
    def detect_brand(self, title):
        title_lower = title.lower()

        sorted_brands = sorted(self.known_brands, key=len, reverse=True)
        
        for brand in sorted_brands:
            if ' ' in brand:
                if brand in title_lower:
                    return brand.title()
            else:
                pattern = r'\b' + re.escape(brand) + r'\b'
                if re.search(pattern, title_lower):
                    return brand.title()
        
        return "None" #else return 'None'
    
    def translate_query(self, query, target_market):
        if target_market not in self.market_languages:
            return query

        target_lang = self.market_languages[target_market]
        if target_lang == 'en':
            return query
        
        try: 
            translated = GoogleTranslator(source='en', target = target_lang).translate(query)
        except:
            return query
        
        cleaned = self.clean_translation(translated, target_lang)
        return cleaned
    

    def clean_translation(self, text: str, lang: str) -> str:
        CLEAN_RULES = {
            "FR": [
                ("de costume", "costume"),
                ("combinaison", "costume"),
                ("hommes", "homme"),
                ("vieux", "vintage"),
                ("de homme", "homme"),
                ("pour homme", "homme"),
                ("pour femme", "femme"),
                ("dame", "femme"),
                ("femmes", "femme"),
            ],
            "IT": [
                ("tuta", "abito"),
                ("di uomini", "uomo"),
                ("signora", "donna"),
                ("uomini", "uomo"),
                ("vecchio", "vintage"),
            ],
            "DE": [
                ("Männer", "Herren"),
                ("Frauen", "Damen"),
                ("für Männer", "Herren"),
                ("alt", "vintage"),
                ("jahrgang", "vintage"),
            ]
        }
        rules = CLEAN_RULES.get(lang.upper(), [])
        for bad, good in rules:
            text = text.replace(bad, good)
        return text.strip()