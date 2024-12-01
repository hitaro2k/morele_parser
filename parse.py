import requests
from lxml import html
import re
import csv
import os

def connection(user_link, page):
    url = f'{user_link}{page}/'
    response = requests.get(url)
    if response.status_code == 200:
        return html.fromstring(response.content)
    return None

def parse_page(htmlDoc):
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
            "link": f"https://www.morele.net{href}",
            "name": text,
            "price": price,
            "views": view
        }
        cart_arr.append(cart)

    return cart_arr

def parse_and_generate_excel(user_link , user_page):
    cart_arr = []
    page = 1
    goal_page = user_page 

    while page <= goal_page:
        print(f"Parsing page {page}...")
        htmlDoc = connection(user_link, page)
        if htmlDoc is None or len(htmlDoc) == 0:
            print(f"Error loading page {page}.")
            break

        current_page_data = parse_page(htmlDoc)
        if not current_page_data:
            break

        cart_arr.extend(current_page_data)
        page += 1

 
    csv_filename = "static/laptops.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Link", "Name", "Price", "Views"])

        for item in cart_arr:
            writer.writerow([item["link"], item["name"], item["price"], item["views"]])

    return csv_filename
