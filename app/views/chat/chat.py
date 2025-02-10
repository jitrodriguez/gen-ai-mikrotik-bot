import streamlit as st


class ChatView:
    def __init__(self):
        self.container = None
        self.chat_input = None

    def draw_messages(self, messages):
        self.container = st.container(height=300)
        with self.container:
            for message in messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    def get_user_input(self, placeholder, disabled, on_submit):
        return st.chat_input(placeholder, disabled=disabled, on_submit=on_submit)

    def additional_data(self):
        # self.container.write("Additional data")
        pass
