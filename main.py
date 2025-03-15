import streamlit as st
from app.controllers.chat_controller import ChatController
from app.controllers.sidebar_controller import SidebarController
from app.models.database import SQLiteDB
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