class ProductModel:
    def __init__(self, conn):
        self.conn = conn

    def get_top_n_products(self, n):
        query = """
            SELECT id, name, image, code, price FROM products
            LIMIT :n
        """
        with self.conn.session as s:
            result = s.execute(query, params={"n": n})
            rows = result.fetchall()
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
        with self.conn.session as s:
            result = s.execute(
                """
                SELECT * FROM products
                WHERE id = :product_id
            """,
                {"product_id": product_id},
            )
            row = result.fetchone()

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

    def search_products(self, search_term, max_results=100):
        with self.conn.session as s:
            query = """
                SELECT id, name, image, code, price FROM products
                WHERE name LIKE :search_term OR description LIKE :search_term
                LIMIT :max_results
            """
            result = s.execute(
                query,
                params={"search_term": f"%{search_term}%", "max_results": max_results},
            )
            rows = result.fetchall()
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
