import streamlit as st
from app.controllers.chat_controller import ChatController
from app.controllers.sidebar_controller import SidebarController
from app.models.database import SQLiteDB

st.set_page_config(layout="wide", page_title="Mikrotik Bot", page_icon="🤖")

# Crear una instancia de la base de datos
db = SQLiteDB("app/database/database.db")
db.connect()

conn = st.connection('database', type='sql')

# Dividir en columnas
row2 = st.container()

with row2:
    with st.container(border=False):
        # Mostrar el chat
        chat_controller = ChatController(db)
        chat_controller.start()

with st.sidebar:
    sidebar_controller = SidebarController(conn)
    sidebar_controller.start()

# Cerrar la conexión a la base de datos al final
db.close()