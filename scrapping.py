from app.controllers.data_controller import DataController

def main():
    db_path = './app/database/database.db'
    data_controller = DataController(db_path)
    products_json = data_controller.fetch_products()
    data_controller.close_db()
    # Aquí puedes hacer algo con el JSON de productos, como guardarlo en un archivo

if __name__ == "__main__":
    main()