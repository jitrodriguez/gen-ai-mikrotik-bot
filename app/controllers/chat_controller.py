import streamlit as st
from app.models.chat_model import ChatModel
from app.views.chat.chat import ChatView
from app.views.chat.context import ContextView
import time


class ChatController:
    def __init__(self):
        self.chat_model = ChatModel()
        self.chat_view = ChatView()
        self.context_view = ContextView()

    def start(self):
        self.display_context()
        self.display_chat()

    def display_context(self):
        self.context_view.draw()

    def display_chat(self):
        INPUT_PLACEHOLDER = "Enviar Mensaje ..."
        self.chat_view.draw_messages(self.chat_model.get_messages())

        if prompt := self.chat_view.get_user_input(
            INPUT_PLACEHOLDER,
            self.chat_model.is_input_disabled(),
            self.disable_callback,
        ):
            self.chat_model.add_message("user", prompt)

            response = f"Echo: {prompt}"
            self.chat_model.add_message("assistant", response)

            st.rerun()
        # if st.button("Additional data"):
        #     self.chat_view.additional_data()
        #     time.sleep(5)
        #     st.success("Done!")

    def disable_callback(self):
        self.chat_model.disable_input()
