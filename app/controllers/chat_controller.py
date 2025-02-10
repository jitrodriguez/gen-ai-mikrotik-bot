import streamlit as st
from app.models.chat_model import ChatModel
from app.views.chat.chat import ChatView
from app.views.chat.context import ContextView

class ChatController:
    def __init__(self, conn):
        self.chat_model = ChatModel()
        self.chat_view = ChatView()
        self.context_view = ContextView()
        self.conn = conn  # Añadir la base de datos como atributo

    def start(self):
        self.display_context()
        self.display_chat()

    def display_context(self):
        products = self.chat_model.get_context_products()
        self.context_view.draw(products=products,delete_callback=self.delete_product_context)

    def delete_product_context(self, index):
        self.chat_model.delete_context_product(index)

    def display_chat(self):
        INPUT_PLACEHOLDER = "Enviar Mensaje ..."
        self.chat_view.draw_messages(self.chat_model.get_messages())

        if prompt := self.chat_view.get_user_input(
            INPUT_PLACEHOLDER,
            self.chat_model.is_input_disabled(),
            self.disable_callback,
        ):
            self.chat_model.add_message("user", prompt)
            response = self.generate_response(prompt)
            self.chat_model.add_message("assistant", response)
            st.rerun()

    def generate_response(self, prompt):
        # Lógica para generar la respuesta del asistente
        return f"Echo: {prompt}"

    def disable_callback(self):
        self.chat_model.disable_input()