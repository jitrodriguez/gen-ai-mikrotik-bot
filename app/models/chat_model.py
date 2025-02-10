import streamlit as st

class ChatModel:
    def __init__(self):
        if "messages" not in st.session_state:
            response = 'Hola, soy un bot especializado en mikrotik. ¿En qué puedo ayudarte?'
            st.session_state.messages = [{"role": "assistant", "content": response, "payload": None, "message_number": 0}]
        if "input_disabled" not in st.session_state:
            st.session_state.input_disabled = False
        if "message_counter" not in st.session_state:
            st.session_state.message_counter = 0

    def get_messages(self):
        return st.session_state.messages

    def add_message(self, role, content):
        st.session_state.message_counter += 1
        st.session_state.messages.append({
            "role": role,
            "content": content,
            "payload": None,
            "message_number": st.session_state.message_counter
        })

    def is_input_disabled(self):
        return st.session_state.input_disabled

    def disable_input(self):
        # st.session_state.input_disabled = True
        pass

    def enable_input(self):
        st.session_state.input_disabled = False