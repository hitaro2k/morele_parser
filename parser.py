import requests
from lxml import html
import re
import csv
import json

def connection(user_link, page):
    try:
        url = f'{user_link}{page}/'
        response = requests.get(url)
        response.raise_for_status()
        return html.fromstring(response.content)
    except requests.exceptions.RequestException as e:
        return None

def parse_page(htmlDoc):
    try:
        cart_arr = []
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
                "link": f"https://www.morele.net{href}" if href else "N/A",
                "name": text if text else "N/A",
                "price": price if price else "N/A",
                "views": view if view else "N/A"
            }
            cart_arr.append(cart)

        return cart_arr
    except Exception as e:
        return []

def parse_and_generate_excel(user_link, user_page):
    try:
        cart_arr = []
        page = 1
        goal_page = user_page 
        csv_filename = "static/laptops.csv"
        
        while page <= goal_page:
            try:
                htmlDoc = connection(user_link, page)
                if htmlDoc is None or len(htmlDoc) == 0:
                    break

                current_page_data = parse_page(htmlDoc)
                if not current_page_data:
                    break

                cart_arr.extend(current_page_data)
                page += 1
            except Exception as e:
                page += 1  
        
        if len(cart_arr) == 0:
            print("empty")
            return None
        else:
            try:
                with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file, delimiter=";")
                    writer.writerow(["Link", "Name", "Price", "Views"])

                    for item in cart_arr:
                        writer.writerow([item["link"], item["name"], item["price"], item["views"]])
                return csv_filename
            except IOError as e:
                print("Файл закрыт куда ты пытаешься сохранить")
                return None
    except Exception as e:
        return None
