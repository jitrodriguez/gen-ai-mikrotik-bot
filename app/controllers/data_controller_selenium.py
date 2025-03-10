from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
from app.models.database import SQLiteDB

class DataControllerSelenium:
    def __init__(self, db_path):
        self.base_url = 'https://mikrotik.com'
        self.url = f'{self.base_url}/products/'
        self.db = SQLiteDB(db_path)
        self.db.connect()
        self.db.create_product_table()

        # Configurar Selenium WebDriver
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Ejecutar en modo headless
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def fetch_products(self):
        # Realizar la solicitud HTTP con Selenium
        self.driver.get(self.url)

        # Desplazarse hacia abajo hasta que no se carguen más productos
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Esperar a que la página cargue
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Encontrar todos los productos
        products = self.driver.find_elements(By.CLASS_NAME, 'product')

        # Lista para almacenar la información de los productos
        product_list = []

        # Extraer la información de cada producto
        for product in products:
            product_info = {}
            product_info['id'] = product.get_attribute('data-id')
            product_info['name'] = product.get_attribute('data-name')
            product_info['code'] = product.get_attribute('data-code')
            product_info['image'] = product.find_element(By.TAG_NAME, 'img').get_attribute('data-src')
            product_info['url'] = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
            product_info['description'] = product.find_element(By.TAG_NAME, 'p').text.strip()
            product_info['price'] = product.find_element(By.CLASS_NAME, 'price').text.strip()

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
        self.driver.quit()