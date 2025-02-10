import streamlit as st
from app.controllers.chat_controller import ChatController
from app.controllers.sidebar_controller import SidebarController
import time
# from app.views.ui_view import display_ui

st.set_page_config(layout="wide",page_title="Mikrotik Bot",page_icon="🤖")

# Dividir en columnas

row2 = st.container()

with row2:
    with st.container( border=False):
        # Mostrar el chat
        chat_controller = ChatController()
        chat_controller.start()
with st.sidebar:
    sidebar_controller = SidebarController()
    sidebar_controller.start()
    # with st.spinner("Loading..."):
    #     time.sleep(5)
    # st.success("Done!")
