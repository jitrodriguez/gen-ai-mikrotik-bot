import streamlit as st

class ChatModel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChatModel, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if "messages" not in st.session_state:
            response = 'Hola, soy un bot especializado en mikrotik. ¿En qué puedo ayudarte?'
            st.session_state.messages = [{"role": "assistant", "content": response, "payload": None, "message_number": 0}]
        if "input_disabled" not in st.session_state:
            st.session_state.input_disabled = False
        if "message_counter" not in st.session_state:
            st.session_state.message_counter = 0
        if "context_products" not in st.session_state:
            st.session_state.context_products = []

    def get_messages(self):
        return st.session_state.messages
    
    def add_product_to_context(self, product):
        products = st.session_state.context_products
        total_products = len(products)
        current_products = [p.get('id') for p in products]
        if product.get('id') in current_products:
            st.toast("El producto ya está en la conversación", icon=":material/error:")
            return
        # allow only 4 products
        if total_products < 4:
            st.session_state.context_products.append(product)
        else:
            st.toast("Solo puedes agregar 4 productos a la conversación", icon=":material/error:")

    def delete_context_product(self, index):
        # remove from specific index
        products = st.session_state.context_products
        print(index)
        print([p.get('id') for p in products])
        products.pop(index)
        print([p.get('id') for p in products])


    def get_context_products(self):
        return st.session_state.context_products


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