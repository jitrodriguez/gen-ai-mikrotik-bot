import streamlit as st
from app.views.components.product import Product

class SuggestView:
    def __init__(self):
        self.container = None
        # self.products = [{
        #     "name": "css318-16g-2s 2Bin",
        #     "price": 100,
        #     "model": "Modelo 1",
        #     "description": "Descripcion 1",
        #     "image": "https://cdn.mikrotik.com/web-assets/rb_images/2408_m.png"
        # },
        # {
        #     "name": "css318-16g-2s 2Bin",
        #     "price": 100,
        #     "model": "Modelo 2",
        #     "description": "Descripcion 2",
        #     "image": "https://cdn.mikrotik.com/web-assets/rb_images/2408_m.png"
        # },
        # {
        #     "name": "css318-16g-2s 2Bin",
        #     "price": 100,
        #     "model": "Modelo 3",
        #     "description": "Descripcion 3",
        #     "image": "https://cdn.mikrotik.com/web-assets/rb_images/2408_m.png"
        # },
        # {
        #     "name": "css318-16g-2s 2Bin",
        #     "price": 100,
        #     "model": "Modelo 4",
        #     "description": "Descripcion 4",
        #     "image": "https://cdn.mikrotik.com/web-assets/rb_images/2408_m.png"
        # }]
        # self.products = products
        self.normal_text = "black"

    def centered_text(self,text, font_size=16,bold=False):
        st.markdown(f"<p style='text-align: center; font-size: {font_size}px; font-weight: {'bold' if bold else 'normal'};'>{text}</p>", unsafe_allow_html=True)
    def draw(self,products=[],add_callback=None):
        self.centered_text("Productos sugeridos", font_size=14, bold=True)
        self.centered_text("Recuerda que todas las comparaciones se hacen de acuerdo a los productos agregados a la conversación", font_size=14, bold=False)
        self.container = st.container(border=True)
        with self.container:
            if len(products) > 0:
                cols = st.columns(4, border=False, vertical_alignment="center")
                for i, product in enumerate(products[:4]):
                    with cols[i]:
                        self.draw_product(product, f"{i}-suggest-product",add_callback=add_callback)

    def draw_product(self,product,id,add_callback=None):
        product = Product(
            name=product.get("name", ""),
            model=product.get("model", ""),
            description=product.get("description", ""),
            image=product.get("image", ""),
            secondary_button_label="Agregar a la conversación",
            secondary_button_callback=lambda p=product: add_callback(p)
        )
        product.draw(id=id)