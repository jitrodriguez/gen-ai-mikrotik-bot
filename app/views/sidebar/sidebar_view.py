import streamlit as st
from app.views.components.product import Product


class SidebarView:
    def __init__(self):
        pass
    def display_products(self, products, primary_button_callback = None, secondary_button_callback=None, tertiary_button_callback=None):
        st.write("Productos")
        with st.container(height=400, border=False):
            for product in products:
                product_view = Product(
                    name=product['name'],
                    image=product['image'],
                    secondary_button_label='Agregar a la conversación',
                    secondary_button_callback=lambda: secondary_button_callback(product),
                    tertiary_button_label='Ver más información',
                    tertiary_button_callback=lambda: tertiary_button_callback(product),
                )
                product_view.draw(f'{product["id"]}-product')

    def display_search_bar(self):
        st.text_input("Buscar Productos")
