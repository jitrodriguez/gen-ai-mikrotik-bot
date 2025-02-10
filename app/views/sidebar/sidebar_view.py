import streamlit as st
from app.views.components.product import Product


class SidebarView:
    def __init__(self):
        pass

    def display_products(self, products, primary_button_callback=None, secondary_button_callback=None, tertiary_button_callback=None):
        total_products = len(products)
        st.write(f"Productos ({total_products})")
        with st.container(height=500, border=True):
            for product in products:
                product_view = Product(
                    name=product.get('name', ''),
                    image=product.get('image', ''),
                    secondary_button_label='Agregar a la conversación',
                    secondary_button_callback=lambda p=product: secondary_button_callback(p),
                    tertiary_button_label='Ver más información',
                    tertiary_button_callback=lambda p=product: tertiary_button_callback(p),
                )
                product_view.draw(f'{product["id"]}-product')

    def display_search_bar(self):
        result = st.text_input("Buscar Productos")
        return result