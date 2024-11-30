import requests
from lxml import html
import re  
import json

def connection(page):
    url = f'https://www.morele.net/kategoria/laptopy-31/,,,,,,,,0,,,,/{page}/'
    response = requests.get(url)
    if response.status_code == 200:
        return html.fromstring(response.content)
    return None

def parse_page(htmlDoc):
    cart_arr = []
    print(htmlDoc)
    products = htmlDoc.xpath("//a[contains(@class, 'productLink')]")
    price_elements = htmlDoc.xpath('//div[contains(@class, "price-new")]')
    views_elements = htmlDoc.xpath('//div[contains(@class, "cat-product-sold")]')

    
    all_prices = []
    for price_element in price_elements:
        prices_text = price_element.xpath("text()")
        if prices_text:
            all_prices.extend([price.strip() for price in prices_text if price.strip()])

   
    all_views = []
    for view_element in views_elements:
        view_text = view_element.xpath("text()")
        if view_text:
            for view in view_text:
                view = view.strip()
                if view:
                    match = re.search(r'\d+', view)  
                    if match:
                        all_views.append(match.group(0))


    for product, price, view in zip(products, all_prices, all_views):
        href = product.xpath("@href")[0] if product.xpath("@href") else None
        text = product.xpath("text()")[0].strip() if product.xpath("text()") else None
        
        cart = {
            "link": href,
            "name": text,
            "price": price,
            "views": view 
        }
        cart_arr.append(cart)

    return cart_arr

def most_buying(arr):
    max_current_int = int(arr[0]["views"])
    max_views_lap = arr[0]
    for el in arr:
        int_views = int(el["views"])
        if int_views > max_current_int:
            max_views_lap = el
            max_current_int = int_views
    return max_views_lap


cart_arr = []
page = 1

while page != 5:
    print(f"Парсинг страницы {page}...")
    htmlDoc = connection(page)
    if htmlDoc is None or len(htmlDoc) == 0:
        print(f"Ошибка загрузки страницы {page}. Прекращаем.")
        break

    current_page_data = parse_page(htmlDoc)
    if not current_page_data:  
        print("Товары на странице не найдены. Парсинг завершён.")
        break

    cart_arr.extend(current_page_data)  
    page += 1  


with open('laptops.json', 'w', encoding='utf-8') as file:
    json.dump(cart_arr, file, ensure_ascii=False, indent=4)

print(f"Парсинг завершён. Всего товаров собрано: {len(cart_arr)}")
