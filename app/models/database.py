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

    def get_products(self, search_term):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT * FROM products
                WHERE name LIKE ? OR code LIKE ? OR description LIKE ?
                """,
                (
                    "%" + search_term + "%",
                    "%" + search_term + "%",
                    "%" + search_term + "%",
                ),
            )
            return cursor.fetchall()

    def get_top_n_products(self, n):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT id,name,image,code,price FROM products
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
                    "price": row[6],
                }
                return product
            else:
                return None

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None