from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import concurrent.futures
from app.models.database import SQLiteDB
from app.models.specifications import SQLiteDB2
import threading
import requests
from bs4 import BeautifulSoup

class DataControllerSelenium:
    def __init__(self, db_path):
        self.base_url = 'https://mikrotik.com'
        self.url = f'{self.base_url}/products/'
        self.db = SQLiteDB(db_path)
        self.db2 = SQLiteDB2(db_path)
        self.db.connect()
        self.db.create_product_table()
        self.db.create_category_table()
        self.db.create_product_category_table()
        self.db2.connect()
        self.db2.create_all_tables()
        self.products = {}

        # Configurar Selenium WebDriver
        self.chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Ejecutar en modo headless
        # self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)

    def fetch_categories(self):
        # Realizar la solicitud HTTP con Selenium
        self.driver.get(self.url)
        # Esperar a que la página cargue
        time.sleep(2)

        # Encontrar todas las categorías
        category_elements = self.driver.find_elements(By.CSS_SELECTOR, 'ul.categories li a')
        categories = [{'name': elem.text, 'url': elem.get_attribute('href')} for elem in category_elements]

        return categories

    def fetch_categories_not_selenium(self):
        response = requests.get(self.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        category_elements = soup.select('ul.categories li a')
        categories = [{'name': elem.get_text(strip=True), 'url': elem['href']} for elem in category_elements]
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

    def fetch_products_not_selenium(self, category):
        category_name = category['name']
        category_url = category['url']
        category_id = category['id']
        
        # Realizar la solicitud HTTP con requests
        response = requests.get(category_url)
        response.raise_for_status()
        
        # Analizar el contenido HTML con BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f'Fetching {category_name} from {category_url}')
        
        # Encontrar todos los productos
        product_elements = soup.select('.product')
        print(f'Found {len(product_elements)} products')
        
        # Extraer la información de cada producto
        for product in product_elements:
            product_id = product['data-id']
            if product_id in self.products:
                self.products[product_id]['categories'].update({category_id})
            else:
                product_info = {
                    'id': product_id,
                    'name': product['data-name'],
                    'code': product['data-code'],
                    'image': product.find('img')['data-src'],
                    'url': product.find('a')['href'],
                    'description': product.find('p').get_text(strip=True),
                    'price': product.find(class_='price').get_text(strip=True),
                    'categories': {category_id}
                }
                self.products[product_id] = product_info

    def fetch_all_products(self):
        categories = self.fetch_categories_not_selenium()
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
            self.fetch_products_not_selenium(category)

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

    def fetch_product_specifications(self, product_id, chrome_options, all_specs_lock):
        print(f'Fetching specifications for product {product_id}')
        product = self.db.get_product(product_id)
        # Crear un nuevo driver para cada hilo con la misma configuración
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            driver.get(product['url'])

            rows = driver.find_element(By.CSS_SELECTOR, 'div table.product-table tbody tr')
            # rows = specifications_table.find_elements(By.TAG_NAME, 'tr')
            specifications = []
            thread_specs = set()
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, 'td')
                rare_specifications = ['vswr','max_out_per_port_output_(input_18_30_v)','2ghz','5ghz','matching']

                if len(tds) >= 2:
                    specifications.append({'key': tds[0].get_attribute('innerText'), 'value': tds[1].get_attribute('innerText')})
                    # replace spaces with underscores and convert to lowercase and also - to _
                    specification_name = tds[0].get_attribute('innerText').lower().replace(' ', '_').replace('-', '_')
                    if specification_name in rare_specifications:
                        print(f'Rare specification found: {specification_name} in product {product_id}')
                    thread_specs.add(specification_name)

            # Actualiza el conjunto compartido de manera segura
            with all_specs_lock:
                self.all_possible_specifications.update(thread_specs)

            return specifications
        except Exception as e:
            print(f'Error fetching specifications for product {product_id}: {e}')
        finally:
            driver.quit()  # Cierra el driver al finalizar

    def fetch_product_specifications_not_selenium(self,product_url, product_id, all_specs_lock):
        db2 = SQLiteDB2('./app/database/database_test.db')
        db2.connect()
        try:
            response = requests.get(product_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            specifications_table = soup.select_one('div#specifications table.product-table tbody')
            rows = specifications_table.find_all('tr')
            specifications = {}

            thread_specs = set()
            rare_specifications = ['vswr','reflector','purpose','2ghz','5ghz','matching','ip','sfp+_ports','max_power_consumption','max_power_consumption_without_attachments','number_of_1g_2_5g_5g_10g_ethernet_ports']
            labels = {
                    'vswr': 'Voltage Standing Wave Ratio (VSWR)',
                    'max_out_per_port_output_(input_18_30_v)': 'Max out per port output (input 18-30 V)',
                    '2ghz': 'Allow 2GHz',
                    '5ghz': 'Allow 5GHz',
                    'matching': 'Matching',
                    'ip': 'IP (International Protection)'
                }
            equivalents = {
                '2ghz': 'allow_2ghz',
                '5ghz': 'allow_5ghz',
                'sfp+_ports': 'sfp_plus_ports',
                'size_of_ram': 'size_of_ram_mb',
                'ip': 'ip_protection',
                'storage_size':'storage_size_mb',
                '10_100_1000_ethernet_ports':'number_10_100_1000_ethernet_ports',
            }
            for row in rows:
                tds = row.find_all('td')
                if len(tds) >= 2:
                    key = tds[0].get_text(strip=True)
                    value = tds[1].get_text(strip=True)
                    if value.lower() == 'yes':
                        value = 1
                    elif value.lower() == 'no':
                        value = 0

                    # specifications.append({'key': key, 'value': value})
                    specification_name = key.lower().replace(' ', '_').replace('-', '_').replace('.','_').replace('/','_')
                    if specification_name in rare_specifications:
                        print(f'Rare specification found: {specification_name} in product {product_url}')
                    if specification_name in equivalents:
                        specification_name = equivalents[specification_name]
                    specifications[specification_name] = value
                    thread_specs.add(specification_name)

            # Actualiza el conjunto compartido de manera segura
            # with all_specs_lock:
                # self.all_possible_specifications.update(thread_specs)
            db2.insert_or_update_tech_specs(product_id, specifications)
            db2.insert_or_update_connectivity_specs(product_id, specifications)
            db2.insert_or_update_wireless_specs(product_id, specifications)
            db2.insert_or_update_power_specs(product_id, specifications)
            db2.insert_or_update_physical_specs(product_id, specifications)

            return specifications
        except Exception as e:
            print(f'Error fetching specifications for product {product_url}: {e}')
            raise e
        finally:
            db2.close()

    def fetch_products_info(self):
        self.all_possible_specifications = set()
        all_specs_lock = threading.Lock()
        products = self.db.get_top_n_products(500)

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            print('Fetching product specifications...')

            futures = [executor.submit(
                self.fetch_product_specifications_not_selenium,
                product['url'],
                product['id'],
                all_specs_lock
            ) for product in products]
            concurrent.futures.wait(futures)

        for specification in self.all_possible_specifications:
            print(specification)
        print('Finished fetching product specifications')
        print('Total specifications:', len(self.all_possible_specifications))
        self.db2.close()

    def separate_specifications(self, specifications):
        tech_specs = [
            'cpu',
            'cpu_core_count',
            'cpu_threads_count',
            'cpu_nominal_frequency',
            'cpu_temperature_monitor',
            'architecture',
            'chipset',
            'switch_chip_model',
            'plc_chipset',
            'storage_size',
            'storage_type',
            'size_of_ram_mb',
            'mtbf'
        ]

        connectivity_specs = [
            '10_100_1000_ethernet_ports',
            'number_of_1g_ethernet_ports_with_poe_out',
            'number_of_1g_2_5g_5g_10g_ethernet_ports',
            'sfp_ports',
            'sfp+_ports',
            'port_to_port_isolation',
            'operating_system'
        ]

        wireless_specs = [
            'wi_fi_generation',
            'wireless_standards',
            'wireless_2.4_ghz_generation',
            'wireless_5_ghz_generation',
            'wireless_2.4_ghz_chip_model',
            'wireless_5_ghz_chip_model',
            'wireless_2.4_ghz_number_of_chains',
            'wireless_5_ghz_number_of_chains',
            'wireless_2.4_ghz_max_data_rate',
            'wireless_5_ghz_max_data_rate',
            'wifi_speed',
            'dbi',
            'beamwidth',
            'cross_polarization',
            'polarization',
            'antenna_header_count',
            'allow_2ghz',
            'allow_5ghz',
            'matching',
            'vswr',
        ]

        power_specs = [
            'max_power_consumption',
            'max_power_consumption_without_attachments',
            'power_rating',
            'current',
            'output_power',
            'output_voltage',
            'input_voltage',
            'dc_jack_input_voltage',
            'poe_in',
            'poe_out',
            'poe_out_ports',
            'poe_in_input_voltage',
            'max_out_per_port_output_(input_18_30_v)',
            'max_out_per_port_output_(input_30_57_v)'
        ]

        physical_specs = [
            'dimensions',
            'diameter_x_depth',
            'weight',
            'packaged_weight',
            'material',
            'color',
            'outdoor_rating',
            'ip',
            'wind_load_(125_mph)',
            'wind_survivability',
            'can_be_used_indoors',
            'can_be_used_outdoors'
        ]


    def close_db(self):
        self.db.close()
        # self.driver.quit()