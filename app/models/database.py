import sqlite3

class SQLiteDB:
    _instance = None

    def __new__(cls, db_path):
        if cls._instance is None:
            cls._instance = super(SQLiteDB, cls).__new__(cls)
            cls._instance.db_path = db_path
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)

    def create_product_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    code TEXT,
                    image TEXT,
                    url TEXT,
                    description TEXT,
                    price TEXT
                )"""
            )

    def insert_product(self, product):
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO products (id, name, code, image, url, description, price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    product["id"],
                    product["name"],
                    product["code"],
                    product["image"],
                    product["url"],
                    product["description"],
                    product["price"],
                ),
            )

    def get_products(self, search_term, top_n=5):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT id, name, image, code, price FROM products
                WHERE name LIKE ? OR code LIKE ?
                LIMIT ?
                """,
                (f"%{search_term}%", f"%{search_term}%", top_n),
            )
            rows = cursor.fetchall()
            products = []
            for row in rows:
                product = {
                    "id": row[0],
                    "name": row[1],
                    "image": row[2],
                    "code": row[3],
                    "price": row[4]
                }
                products.append(product)
            return products

    def search_products_by_category(self, category_id, top_n=5, order_by=None, order='ASC', price_range=None):
        with self.connection:
            cursor = self.connection.cursor()
            query = """
                SELECT p.id, p.name, p.image, p.code, p.price, p.categories
                FROM products p
                JOIN product_category pc
                ON p.id = pc.product_id
                WHERE pc.category_id = ?
            """
            params = [category_id]
            
            if price_range:
                query += " AND p.price BETWEEN ? AND ?"
                params.extend(price_range)
            
            if order_by:
                query += f" ORDER BY {order_by} {order}"
            
            query += f" LIMIT {top_n}"
            
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            products = []
            for row in rows:
                product = {
                    "id": row[0],
                    "name": row[1],
                    "image": row[2],
                    "code": row[3],
                    "price": row[4]
                }
                products.append(product)
            return products

    def get_top_n_products(self, n):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT id,name,image,code,price,url FROM products
                LIMIT ?
            """,
                (n,),
            )
            rows = cursor.fetchall()
            products = []
            for row in rows:
                product = {
                    "id": row[0],
                    "name": row[1],
                    "image": row[2],
                    "code": row[3],
                    "price": row[4],
                    "url": row[5]
                }
                products.append(product)
            return products

    def get_product(self, product_id):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT * FROM products
                WHERE id = ?
            """,
                (product_id,),
            )
            row = cursor.fetchone()
            if row:
                product = {
                    "id": row[0],
                    "name": row[1],
                    "code": row[2],
                    "image": row[3],
                    "url": row[4],
                    "description": row[5],
                    "price": row[6]
                }
                return product
            else:
                return None

    def update_product(self, product_info):
        query = '''
        UPDATE products
        SET name = ?, code = ?, image = ?, url = ?, description = ?, price = ?
        WHERE id = ?
        '''
        with self.connection:
            self.connection.execute(
                query,
                (
                    product_info['name'],
                    product_info['code'],
                    product_info['image'],
                    product_info['url'],
                    product_info['description'],
                    product_info['price'],
                    product_info['id']
                )
            )

    def create_category_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    url TEXT
                )"""
            )

    def insert_category(self, category):
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO categories (name, url)
                VALUES (?, ?)
            """,
                (
                    category["name"],
                    category["url"]
                ),
            )

    def get_categories(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT * FROM categories
            """
            )
            rows = cursor.fetchall()
            categories = []
            for row in rows:
                category = {
                    "id": row[0],
                    "name": row[1],
                    "url": row[2]
                }
                categories.append(category)
            return categories

    def update_category(self, category_info):
        query = '''
        UPDATE categories
        SET name = ?, url = ?
        WHERE id = ?
        '''
        with self.connection:
            self.connection.execute(
                query,
                (
                    category_info['name'],
                    category_info['url'],
                    category_info['id'],
                )
            )

    def create_product_category_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS product_category (
                    product_id INTEGER,
                    category_id INTEGER,
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )"""
            )

    def insert_product_category(self, product_id,category_id):
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO product_category (product_id, category_id)
                VALUES (?, ?)
            """,
                (
                    product_id,
                    category_id
                ),
            )

    def delete_product_category(self, product_id, category_id):
        with self.connection:
            self.connection.execute(
                """
                DELETE FROM product_category
                WHERE product_id = ? AND category_id = ?
                """,
                (product_id,category_id,),
            )

    def create_specification_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS specifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT
                )"""
            )
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None