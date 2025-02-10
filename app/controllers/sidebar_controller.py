import streamlit as st
from app.views.sidebar.sidebar_view import SidebarView
from app.models.database import SQLiteDB
import time


class SidebarController:
    def __init__(self):
        self.view = SidebarView()
        self.db = SQLiteDB("app/database/database.db")

    def start(self):
        self.view.display_search_bar()
        self.db.connect()
        products = self.db.get_top_n_products(5)
        self.view.display_products(
            products=products,
            secondary_button_callback=self.add_to_conversation,
            tertiary_button_callback=self.show_more_info,
        )

    def add_to_conversation(self, *args):
        product = args[0]
        print(product)
        pass
    def show_more_info(self, *args):
        product = args[0]
        print(product)
        pass

    def display_chat(self):
        pass

    def disable_callback(self):
        pass
