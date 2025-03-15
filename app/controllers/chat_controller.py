import streamlit as st
from app.models.chat_model import ChatModel
from app.views.chat.chat import ChatView
from app.views.chat.context import ContextView
from langchain_core.messages import HumanMessage
from app.views.chat.suggest import SuggestView

class ChatController:
    def __init__(self, conn):
        self.chat_model = ChatModel()
        self.chat_view = ChatView()
        self.context_view = ContextView()
        self.suggest_view = SuggestView()
        self.conn = conn

    def start(self):
        self.display_context()
        self.display_chat()
        self.display_suggestions()

    def display_context(self):
        products = self.chat_model.get_context_products()
        self.context_view.draw(products=products,delete_callback=self.delete_product_context)

    def delete_product_context(self, index):
        self.chat_model.delete_context_product(index)

    def add_product_context(self, product):
        self.chat_model.add_product_to_context(product)

    def display_chat(self):
        INPUT_PLACEHOLDER = "Enviar Mensaje ..."
        self.chat_view.draw_messages(self.chat_model.get_messages())

        if prompt := self.chat_view.get_user_input(
            INPUT_PLACEHOLDER,
            self.chat_model.is_input_disabled(),
            self.disable_callback,
        ):
            self.chat_view.draw_message({"role": "user", "content": prompt})
            data = self.chat_view.draw_loading("", self.generate_response, prompt)
            # Caso raro que la data llega como string
            if type(data) == str:
                print('data',data)
                st.toast(data)
                return
            self.chat_model.add_message("user", prompt)
            self.chat_model.add_message("assistant", data.get('response'))
            suggestions = data.get('suggestions')
            keep_suggestions = data.get('keep_suggestions',False)
            if not keep_suggestions and suggestions:
                self.chat_model.add_suggestions(suggestions)
            st.rerun()
    def display_suggestions(self):
        suggestions = self.chat_model.get_suggestions()
        self.suggest_view.draw(products=suggestions, add_callback= self.add_product_context)

    def generate_response(self, prompt):
        # Lógica para generar la respuesta del asistente
        messages = self.chat_model.get_messages_for_langgraph()
        messages.append({"message": HumanMessage(prompt)})
        prods = self.chat_model.get_context_products()
        retry_count = 1
        # A veces los inputs fallan y ocurre un problema de pydatanic, se pone reintento de 3 veces
        data = st.session_state.graph.invoke(input={"messages": messages , 'products':prods}, config=st.session_state.config)
        for attempt in range(retry_count):
            try:
                break
            except Exception as e:
                if attempt < retry_count - 1:
                    continue
                else:
                    print(e)
                    st.error(f"Error en la generación de la respuesta: {e}")
                    return {"response":'Error en la generación de la respuesta'}
        last_message = data.get('messages')[-1].get('message')
        keep_suggestions = data.get('keep_suggestions',False)
        products = data.get('suggestions')
        product_list = []
        if products:
            for key,value in products.items():
                product_list.append({
                    "id": key,
                    "code": value.get("code"),
                    "name": value.get("name"),
                    "price": value.get("price"),
                    "model": value.get("model"),
                    "description": value.get("description"),
                    "image": value.get("image")
                })
        if last_message.type == 'ai':
            return { 'response':last_message.content, 'suggestions':product_list, 'keep_suggestions':keep_suggestions}
        else:
            return { 'response':'Conversación finalizada', 'suggestions':product_list, 'keep_suggestions':keep_suggestions}

    def disable_callback(self):
        self.chat_model.disable_input()