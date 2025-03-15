from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict
from langchain_core.messages import AnyMessage
from app.langgraph.tools.search_products_by_category import search_products_by_category
from app.langgraph.tools.search_products_by_connectivity_specs import search_products_by_connectivity_specs
from app.langgraph.tools.search_products_by_power_specs import search_products_by_power_specs

load_dotenv()

class LLMInstance:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMInstance, cls).__new__(cls)
            # Aquí podemos cambiar a cualquier modelo de llm
            cls._instance.main_llm = ChatOllama(model='llama3.2:latest',temperature=0)
            # cls._instance.main_llm = ChatOpenAI(model="gpt-4o",temperature=0)
        return cls._instance

class MyMessageState(TypedDict):
    messages: list[AnyMessage]
    products: list
    suggestions: dict
    keep_suggestions: bool

# Para obtener la instancia única de llm
llm_instance = LLMInstance()
main_llm = llm_instance.main_llm

tools = [search_products_by_category,search_products_by_connectivity_specs,search_products_by_power_specs]