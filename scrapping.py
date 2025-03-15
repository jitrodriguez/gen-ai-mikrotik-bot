from app.controllers.data_controller import DataController
from app.controllers.data_controller_selenium import DataControllerSelenium

def main():
    db_path = './app/database/database_3.db'
    # data_controller = DataController(db_path)
    data_controller = DataControllerSelenium(db_path)
    # products_json = data_controller.fetch_products()
    data_controller.fetch_all_products()
    # data_controller.fetch_product_specifications(745)
    data_controller.fetch_products_info()
    data_controller.close_db()
    # Aquí puedes hacer algo con el JSON de productos, como guardarlo en un archivo

if __name__ == "__main__":
    main()