import requests
from bs4 import BeautifulSoup
import json
from app.models.database import SQLiteDB

class DataController:
    def __init__(self, db_path):
        self.base_url = 'https://mikrotik.com'
        self.url = f'{self.base_url}/products/'
        self.db = SQLiteDB(db_path)
        self.db.connect()
        self.db.create_product_table()

    def fetch_products(self):
        # Realizar la solicitud HTTP
        response = requests.get(self.url)
        html_content = response.content

        # Parsear el contenido HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Encontrar todos los productos
        products = soup.find_all('div', class_='product')

        # Lista para almacenar la información de los productos
        product_list = []

        # Extraer la información de cada producto
        for product in products:
            product_info = {}
            product_info['id'] = product['data-id']
            product_info['name'] = product['data-name']
            product_info['code'] = product['data-code']
            product_info['image'] = product.find('img')['data-src']
            product_info['url'] = product.find('a')['href']
            product_info['description'] = product.find('p').text.strip()
            product_info['price'] = product.find('div', class_='price').text.strip()

            product_list.append(product_info)

            # Insertar el producto en la base de datos
            self.db.insert_product(product_info)

        # Convertir la lista de productos a JSON
        product_json = json.dumps(product_list, indent=4)

        # Imprimir el JSON
        print(product_json)

        return product_json

    def close_db(self):
        self.db.close()