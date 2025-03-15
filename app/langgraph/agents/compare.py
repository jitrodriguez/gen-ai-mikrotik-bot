from app.langgraph.config import main_llm
from app.langgraph.config import MyMessageState
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
import configs as cfg
from typing import Literal
from langgraph.graph import StateGraph, START, END
from app.langgraph.utils import get_products_info


SYSTEM_PROMPT = """
<PERSONA>
Eres un especialista en comparaciones de productos, marcas, modelos, precios, especificaciones técnicas, etc.
A continuación se te dará una lista de los productos que se desean comparar.
Debes proporcionar una comparación clara y concisa de los productos, de acuero a la pregunta del usuario.
</PERSONA>
<PRODUCTOS>
{products}
</PRODUCTOS>
"""

def compare(state: MyMessageState):
    if cfg.print_compare_state:
        print('state on Compare',state)

    if 'products' in state:
        try:
            products = state['products']
            if len(products) < 2:
                state["messages"].append(
                    {
                        'message': AIMessage("Debes agregar al menos 2 productos a la conversación para poder compararlos."),
                        'route_main': False,
                        'keep_suggestions': True
                    }
                )
                return state
        except:
            pass
    products_ids = [p['id'] for p in products]
    products_info = get_products_info(*products_ids)
    last_3_messages = [ m['message'] for m in state["messages"] if m['message'].type != "system" ][-3:]
    messages = [
        SystemMessage(SYSTEM_PROMPT.format(products=products_info)),
        *last_3_messages
    ]
    response = main_llm.invoke(messages)
    content = response.content
    state["messages"].append(
        {
            # se pone AIMessage para que el mensaje sea interpretado como un mensaje de la IA por el model de Ollama
            'message': AIMessage(content),
            'added_by': 'compare',
            'route_main': False
        }
    )
    return state


def compare_conditional_path(state:MyMessageState)->Literal["main","__end__"]:
    last_message = state["messages"][-1]
    route_main = last_message.get('route_main','end')
    if route_main:
        return "main"
    return END