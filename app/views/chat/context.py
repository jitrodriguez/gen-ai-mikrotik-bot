import streamlit as st
from app.views.components.product import Product

class ContextView:
    def __init__(self):
        self.container = None
        self.products = [{
            "name": "css318-16g-2s 2Bin",
            "price": 100,
            "model": "Modelo 1",
            "description": "Descripcion 1",
            "image": "https://cdn.mikrotik.com/web-assets/rb_images/2408_m.png"
        },
        {
            "name": "css318-16g-2s 2Bin",
            "price": 100,
            "model": "Modelo 2",
            "description": "Descripcion 2",
            "image": "https://cdn.mikrotik.com/web-assets/rb_images/2408_m.png"
        },
        {
            "name": "css318-16g-2s 2Bin",
            "price": 100,
            "model": "Modelo 3",
            "description": "Descripcion 3",
            "image": "https://cdn.mikrotik.com/web-assets/rb_images/2408_m.png"
        },
        {
            "name": "css318-16g-2s 2Bin",
            "price": 100,
            "model": "Modelo 4",
            "description": "Descripcion 4",
            "image": "https://cdn.mikrotik.com/web-assets/rb_images/2408_m.png"
        }]
        self.products = []
        self.normal_text = "black"

    def centered_text(self,text, font_size=16,bold=False):
        st.markdown(f"<p style='text-align: center; font-size: {font_size}px; font-weight: {'bold' if bold else 'normal'};'>{text}</p>", unsafe_allow_html=True)
    def draw(self):
        self.centered_text("Productos en la conversación (máximo 4)", font_size=14, bold=True)
        self.container = st.container(border=True)
        with self.container:
            if len(self.products) > 0:
                cols = st.columns(4, border=False, vertical_alignment="center")
                for i, product in enumerate(self.products):
                    with cols[i]:
                        self.draw_product(product, f"{i}-context-product")
            else:
                self.centered_text("Aún no hay productos para mostrar")
                self.centered_text("Puedes buscar productos en la barra lateral o agregarlos desde la conversación", font_size=12)
    def draw_product(self,product,id):
        product = Product(
            name=product["name"],
            model=product["model"],
            description=product["description"],
            image=product["image"],
            secondary_button_label="Eliminar",
            secondary_button_callback=None
        )
        product.draw(id=id)