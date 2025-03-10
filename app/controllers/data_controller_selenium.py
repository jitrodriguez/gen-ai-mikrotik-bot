from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import concurrent.futures
from app.models.database import SQLiteDB
import threading

class DataControllerSelenium:
    def __init__(self, db_path):
        self.base_url = 'https://mikrotik.com'
        self.url = f'{self.base_url}/products/'
        self.db = SQLiteDB(db_path)
        self.db.connect()
        self.db.create_product_table()
        self.db.create_category_table()
        self.db.create_product_category_table()
        self.products = {}

        # Configurar Selenium WebDriver
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Ejecutar en modo headless
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def fetch_categories(self):
        # Realizar la solicitud HTTP con Selenium
        self.driver.get(self.url)
        # Esperar a que la página cargue
        time.sleep(2)

        # Encontrar todas las categorías
        category_elements = self.driver.find_elements(By.CSS_SELECTOR, 'ul.categories li a')
        categories = [{'name': elem.text, 'url': elem.get_attribute('href')} for elem in category_elements]

        return categories

    def fetch_products(self, category):
        category_name = category['name']
        category_url = category['url']
        category_id = category['id']
        # Realizar la solicitud HTTP con Selenium
        self.driver.get(category_url)
        # Esperar a que la página cargue
        time.sleep(2)
        print(f'Fetching {category_name} from {category_url}')

        # Encontrar todos los productos
        products = self.driver.find_elements(By.CLASS_NAME, 'product')

        print(f'Found {len(products)} products')
        # Extraer la información de cada producto
        for product in products:
            product_id = product.get_attribute('data-id')
            # is in self.products, add category
            if product_id in self.products:
                # add to tuple
                self.products[product_id]['categories'].update({category_id})
            else:
                product_info = {}
                product_info['id'] = product_id
                product_info['name'] = product.get_attribute('data-name')
                product_info['code'] = product.get_attribute('data-code')
                product_info['image'] = product.find_element(By.TAG_NAME, 'img').get_attribute('data-src')
                product_info['url'] = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
                product_info['description'] = product.find_element(By.TAG_NAME, 'p').get_attribute('innerText').strip()
                product_info['price'] = product.find_element(By.CLASS_NAME, 'price').get_attribute('innerText').strip()
                product_info['categories'] = {category_id}
                self.products[product_id] = product_info

    def fetch_all_products(self):
        categories = self.fetch_categories()
        # insert categories in db
        # delete first category in array
        categories.pop(0)
        for category in categories:
            print('fetched category:', category)
            self.db.insert_category(category=category)
        # get categories from db
        categories = self.db.get_categories()
        for category in categories:
            print(category)
        if not categories:
            print('No categories found')
            exit()

        for category in categories:
            self.fetch_products(category)

        # Guardar los productos en la base de datos
        for product in self.products.values():
            self.db.insert_product(product=product)
            product_categories = product['categories']
            for category_id in product_categories:
              self.db.insert_product_category(product['id'],category_id)

        # Convertir la lista de productos a JSON
        # product_json = json.dumps(self.products, indent=4)
        print('Proceso finalizado')

        # Imprimir el JSON
        # print(product_json)

        return self.products

    def fetch_product_specifications(db, product_id, chrome_options, all_specs_lock):
        product = db.get_product(product_id)
        # Crear un nuevo driver para cada hilo con la misma configuración
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        try:
            driver.get(product['url'])
            time.sleep(2)
            
            specifications_table = driver.find_element(By.CSS_SELECTOR, 'div#specifications table.product-table tbody')
            rows = specifications_table.find_elements(By.TAG_NAME, 'tr')
            specifications = []
            
            thread_specs = set()
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, 'td')
                if len(tds) >= 2:
                    specifications.append({'key': tds[0].get_attribute('innerText'), 'value': tds[1].get_attribute('innerText')})
                    specification_name = tds[0].get_attribute('innerText').lower().replace(' ', '_')
                    thread_specs.add(specification_name)
            
            # Actualiza el conjunto compartido de manera segura
            with all_specs_lock:
                self.all_possible_specifications.update(thread_specs)
                
            return specifications
        finally:
            driver.quit()  # Cierra el driver al finalizar

    def fetch_products_info(self):
        self.all_possible_specifications = set()
        all_specs_lock = threading.Lock()
        products = self.db.get_top_n_products(500)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            # Pasa también las chrome_options a cada hilo
            futures = [executor.submit(
                self.fetch_product_specifications, 
                self.db, 
                product['id'], 
                self.chrome_options,  # Asumiendo que chrome_options está disponible como self.chrome_options
                all_specs_lock
            ) for product in products]
            
            concurrent.futures.wait(futures)
        
        for specification in self.all_possible_specifications:
            print(specification)

    def close_db(self):
        self.db.close()
        self.driver.quit()