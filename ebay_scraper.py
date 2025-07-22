import json

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

    # Title score
    if title:
        pass

    #price score
    pass

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
    pass

    #vintage status
    if vintage_status == 'vintage':
        score += 1
    
    return score
