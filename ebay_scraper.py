import os
import json
from api_integration import EbayAPI
from html_generator import create_html

#work in progress: title keyword dictionary
    #"made in italy", "retro", "selvedge"

#findCompletedItem API for historical dataset and prices

script_dir = os.path.dirname(os.path.abspath(__file__))
brands_path = os.path.join(script_dir, "brands.txt")
values_path = os.path.join(script_dir, "item_values.json")

#open brands file
with open(brands_path, "r", encoding="utf-8") as f:
    known_brands = {
        line.strip().lower()
        for line in f
        if line.strip() and not line.strip().startswith('#')
    }

#open json file
with open(values_path, "r", encoding="utf-8") as f:
    item_values = json.load(f)

#default filters
DEFAULT_EXCLUDE_KEYWORDS = ["reseller", "resale", "wholesale", "bulk", "lot", "5 paar", "set", "pack", "bundle", "printed", "S M L", "S M L XL", "barbie", "disney", "mattel", "doll", "toy"]
DEFAULT_EXCLUDE_BRANDS = ["H&M", "Zara", "Primark", "Shein", "Bershka", "Pull&Bear", "Stradivarius", "Forever 21", "ASOS", "Boohoo", "PrettyLittleThing", "Missguided", "New Look", "Gant", "Mango"]
DEFAULT_LIKED_KEYWORDS = ["vintage", "retro", "selvedge", "made in italy", "made in france", "made in japan", "rare", "archive", 
                          "tailored", "alta moda", "archiv", "archivio"]


#basic item type classifer
def classify_item_type(title):
    title_lower = title.lower()
    for item_type in item_values:
        if item_type in title_lower:
            return item_type
    return None

def score(title, price, condition, seller_score, brand, vintage_status):
    
    score = 0

    #title/price score
    item_type = classify_item_type(title)
    if item_type:
        good_price = item_values[item_type]
        price_ratio = good_price / price if price > 0 else 0

        if price_ratio >= 1.5:
            score +=5 #good deal
        elif price_ratio >= 1.2:
            score += 3
        elif price_ratio >= 0.9:
            score += 1
        elif price_ratio >= 0.7:
            score -= 1
        else:
            score -= 3 #way overpriced

    #condition score
    #condition score
    if condition in ['NEW', 'NEW_OTHER', 'NEW_WITH_DEFECTS']:
        score -= 3  # Penalize new items 
    elif condition in ['USED_EXCELLENT', 'PRE_OWNED_EXCELLENT', 'LIKE_NEW']:
        score += 4  # Best used condition
    elif condition in ['USED_VERY_GOOD', 'USED_GOOD']:
        score += 3  # Good used condition
    elif condition in ['SELLER_REFURBISHED', 'CERTIFIED_REFURBISHED', 'USED_ACCEPTABLE']:
        score += 2  # Still usable
    elif condition == 'FOR_PARTS_OR_NOT_WORKING':
        score -= 2  # Broken items
    pass

    #seller score
    if seller_score >= 4.0:
        score+=2
    elif seller_score >= 3.5:
        score+=1

    #brand score
    if brand and brand.strip():
        if brand.lower() in known_brands:
            score += 6

    #vintage status
    title_lower = title.lower()
    if vintage_status == 'vintage':
        score += 8
    elif any (keyword.lower() in title_lower for keyword in DEFAULT_LIKED_KEYWORDS):
        score += 6
    
    return score, item_type

def apply_filters(items):
    """Filtering items based on unwanted keywords, brands, and potential resellers."""
    filtered_items = []

    for item in items:
        title_lower = item['title'].lower()
        brand_lower = item['brand'].lower() if item['brand'] != 'None' else ''

        if any (keyword.lower() in title_lower for keyword in DEFAULT_EXCLUDE_KEYWORDS):
                continue
        
        if any (keyword.lower() in title_lower for keyword in DEFAULT_EXCLUDE_BRANDS):
                continue
        
        if any (brand.lower() in brand_lower for brand in DEFAULT_EXCLUDE_BRANDS):
                continue
    
        filtered_items.append(item)
    
    return filtered_items

def search_ebay(query, max_results=600, min_score = 3):
    ebay_api = EbayAPI()

    print(f"Searching eBay markets for '{query}'.")
    results = ebay_api.search_items(query, max_results=max_results, marketplace = ['EBAY_FR', 'EBAY_IT', 'EBAY_DE', 'EBAY_AT'])

    items = results['itemSummaries']
    scored_items = []

    for item in items:
        item_data = ebay_api.extract_item_data(item)

        if item_data:
            item_score, item_type = score(
                item_data['title'],
                item_data['price'],
                item_data['condition'],
                item_data['seller_score'],
                item_data['brand'],
                item_data['vintage_status']
            )

            if item_score >= min_score:
                item_data['score']=item_score
                item_data['item_type'] = item_type
                scored_items.append(item_data)
            
    scored_items.sort(key = lambda x: x['score'], reverse = True)
    filtered_items = apply_filters(scored_items)
    return filtered_items


def main():
    query = input("Enter search query: ")
    results = search_ebay(query, max_results = 600, min_score=3)
    if results:
        create_html(results, "ebay_results.html", query)
    
    print(f"the first items brand is: {results[0]['brand']}")

if __name__ == "__main__":
    main()