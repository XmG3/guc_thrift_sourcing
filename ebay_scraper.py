import json

#work in progress: title keyword dictionary
    #"made in italy", "retro", "selvedge"

#findCompletedItem API for historical dataset and prices

#open brands file
with open("brands.txt", "r", encoding="utf-8") as f:
    known_brands = {
        line.strip().lower()
        for line in f
        if line.strip() and not line.strip().startswith('#')
    }

#open json file
with open("item_values", "r", encoding="utf-8") as f:
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
        score += 1
    
    return score, item_type