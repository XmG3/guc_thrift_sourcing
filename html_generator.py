import os

class HTMLGenerator: 
    def __init__(self, template_path="template.html"):
        self.template_path = template_path
    
    def load_template(self):
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to backup if file not found
            return self.get_backup_template()
    
    def get_backup_template(self):
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eBay Search Results - {{search_term}}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #0064d2;
            text-align: center;
            margin-bottom: 30px;
        }
        .item {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            gap: 20px;
        }
        .item-image {
            flex-shrink: 0;
            width: 150px;
            height: 150px;
        }
        .item-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 8px;
        }
        .item-details {
            flex: 1;
        }
        .item-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        .item-title a {
            text-decoration: none;
            color: #0064d2;
        }
        .item-title a:hover {
            text-decoration: underline;
        }
        .score {
            display: inline-block;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .price {
            font-size: 24px;
            font-weight: bold;
            color: #d32f2f;
            margin-bottom: 10px;
        }
        .details {
            color: #666;
            margin-bottom: 8px;
        }
        .vintage {
            background: #ff9800;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
        }
        .cheap {
            background: #47714A;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
        }
        .no-image {
            background: #eee;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <h1>eBay Search Results{{search_term_display}}</h1>
    <p style="text-align: center; color: #666;">Found {{item_count}} items, sorted by score</p>
    {{items_html}}
</body>
</html>"""

    def generate_item_html(self, item):
        # Handle image
        if item.get('image_url'):
            image_html = f'<img src="{item["image_url"]}" alt="Item image" onerror="this.style.display=\'none\'">'
        else:
            image_html = '<div class="no-image">No Image</div>'
        
        # Handle badges
        badges = ''
        if item.get('vintage_status') == 'vintage':
            badges += '<span class="vintage">🏷️ VINTAGE</span>'
        if item['price'] < 25:
            badges += '<span class="cheap">💰 CHEAP</span>'
        
        return f"""
    <div class="item">
        <div class="item-image">
            {image_html}
        </div>
        <div class="item-details">
            <div class="score">Score: {item['score']}</div>
            <div class="item-title">
                <a href="{item['url']}" target="_blank">{item['title']}</a>
                {badges}
            </div>
            <div class="price">€{item['price']:.2f}</div>
            <div class="details">Condition: {item['condition']}</div>
            <div class="details">Brand: {item.get('brand', 'Unknown')}</div>
        </div>
    </div>"""

    def create_html(self, items, filename = "ebay_results_html", search_term = ""):
        template = self.load_template()
        items_html = ""
        for item in items:
            items_html += self.generate_item_html(item)
        
        search_term_display = f' - {search_term}' if search_term else ''
        
        html_content = template.replace('{{search_term}}', search_term)
        html_content = html_content.replace('{{search_term_display}}', search_term_display)
        html_content = html_content.replace('{{item_count}}', str(len(items)))
        html_content = html_content.replace('{{items_html}}', items_html)
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML creation successful.")        
        return filename

# Convenience function for backward compatibility
def create_html(items, filename="ebay_results.html", search_term=""):
    """Standalone function that uses HTMLGenerator"""
    generator = HTMLGenerator()
    return generator.create_html(items, filename, search_term)