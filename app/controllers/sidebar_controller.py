from app.views.sidebar.sidebar_view import SidebarView
from app.models.product_model import ProductModel
from app.models.chat_model import ChatModel
import streamlit as st


class SidebarController:
    def __init__(self, conn):
        self.view = SidebarView()
        self.conn = conn  # Añadir la base de datos como atributo
        self.product_model = ProductModel(conn)
        self.chat_model = ChatModel()

    def start(self):
        text = self.view.display_search_bar()
        if text:
            products = self.product_model.search_products(text)
        else:
            products = self.product_model.get_top_n_products(10)
        self.view.display_products(
            products=products,
            secondary_button_callback=self.add_to_conversation,
            tertiary_button_callback=self.show_more_info,
        )
    def search_products(self, search_term):
        products = self.product_model.search_products(search_term)
        self.view.display_products(
            products=products,
            secondary_button_callback=self.add_to_conversation,
            tertiary_button_callback=self.show_more_info,
        )
    def add_to_conversation(self, product):
        product_info = self.product_model.get_product(product['id'])
        self.chat_model.add_product_to_context(product_info)

    def show_more_info(self, product):
        # Lógica para mostrar más información del producto
        # print(product)
        pass