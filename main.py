import streamlit as st
from app.controllers.chat_controller import ChatController
from app.controllers.sidebar_controller import SidebarController
import os
from app.langgraph.graph import get_graph
import uuid
import torch

# https://github.com/VikParuchuri/marker/issues/442#issuecomment-2636393925 issue with streamlit and torch
torch.classes.__path__ = []

st.set_page_config(layout="wide", page_title="Mikrotik Bot", page_icon="🤖")

if 'graph' not in st.session_state:
    st.session_state.graph = get_graph()
    st.session_state.messages = []
    st.session_state.config = {"configurable": {"thread_id": str(uuid.uuid4())}}

if 'allow_user' not in st.session_state or st.session_state.allow_user is False:
    secret_key_input = st.text_input("Secret Key", key="secret_key")
    if secret_key_input:
        secret_key = os.getenv("SECRET_KEY")
        st.session_state.allow_user = secret_key == secret_key_input
        if st.session_state.allow_user:
            st.rerun()
else:
    conn = st.connection('database', type='sql')

    # Dividir en columnas
    row2 = st.container()

    with row2:
        with st.container(border=False):
            # Mostrar el chat
            chat_controller = ChatController(conn)
            chat_controller.start()

    with st.sidebar:
        sidebar_controller = SidebarController(conn)
        sidebar_controller.start()

# Cerrar la conexión a la base de datos al final
# db.close()