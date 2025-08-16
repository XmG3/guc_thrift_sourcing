import os
import json
from api_integration import EbayAPI

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
            score += 0
        else:
            score -= 2 #way overpriced

    #condition score
    if condition == 'Gut':
        score += 2
    elif condition == 'Hervorragend':
        score += 3
    elif condition == 'Gebraucht':
        score += 2
    pass

    #seller score
    if seller_score >= 4.0:
        score+=2
    elif seller_score >= 3.5:
        score+=1

    #brand score
    if brand and brand.lower() in known_brands:
        score += 3

    #vintage status
    if vintage_status == 'vintage':
        score += 3
    
    return score, item_type

def search_ebay(query, max_results=200, min_score = 0):
    ebay_api = EbayAPI()

    print(f"Searching eBay.at for '{query}'.")
    results = ebay_api.search_items(query, max_results=max_results)

    items = results['itemSummaries']
    scored_items = []

    for item in items:
        item_data = ebay_api.extract_item_data(item, known_brands)

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
    return scored_items

def create_html(items, filename="ebay_results.html", search_term=""):
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eBay Search Results - {search_term}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #0064d2;
            text-align: center;
            margin-bottom: 30px;
        }}
        .item {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            gap: 20px;
        }}
        .item-image {{
            flex-shrink: 0;
            width: 150px;
            height: 150px;
        }}
        .item-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 8px;
        }}
        .item-details {{
            flex: 1;
        }}
        .item-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }}
        .item-title a {{
            text-decoration: none;
            color: #0064d2;
        }}
        .item-title a:hover {{
            text-decoration: underline;
        }}
        .score {{
            display: inline-block;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .price {{
            font-size: 24px;
            font-weight: bold;
            color: #d32f2f;
            margin-bottom: 10px;
        }}
        .details {{
            color: #666;
            margin-bottom: 8px;
        }}
        .vintage {{
            background: #ff9800;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
        }}
        .no-image {{
            background: #eee;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <h1>eBay Search Results{f' - {search_term}' if search_term else ''}</h1>
    <p style="text-align: center; color: #666;">Found {len(items)} items, sorted by score</p>
"""
    
    for i, item in enumerate(items, 1):
        image_html = ""
        if item.get('image_url'):
            image_html = f'<img src="{item["image_url"]}" alt="Item image" onerror="this.style.display=\'none\'">'
        else:
            image_html = '<div class="no-image">No Image</div>'
        
        vintage_badge = '<span class="vintage">🏷️ VINTAGE</span>' if item.get('vintage_status') == 'vintage' else ''
        
        html_content += f"""
    <div class="item">
        <div class="item-image">
            {image_html}
        </div>
        <div class="item-details">
            <div class="score">Score: {item['score']}</div>
            <div class="item-title">
                <a href="{item['url']}" target="_blank">{item['title']}</a>
                {vintage_badge}
            </div>
            <div class="price">€{item['price']:.2f}</div>
            <div class="details">Condition: {item['condition']}</div>
            <div class="details">Brand: {item.get('brand', 'Unknown')} | Type: {item.get('item_type', 'Unknown')}</div>
            <div class="details">Seller Score: {item['seller_score']:.1f}/5.0</div>
            <div class="details">Location: {item.get('location', 'Unknown')}</div>
        </div>
    </div>
"""
    
    html_content += """
</body>
</html>
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML results created: {filename}")
    print(f"Open {filename} in your browser to view results with clickable links!")

def main():
    query = input("Enter search query: ")
    results = search_ebay(query, max_results = 200, min_score=0)
    if results:
        create_html(results, "ebay_results.html", query)

if __name__ == "__main__":
    main()