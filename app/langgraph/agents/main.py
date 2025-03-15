from app.langgraph.config import main_llm
from typing import TypedDict
from pydantic import Field
from app.langgraph.config import MyMessageState
from app.langgraph.tools.search_products_by_category import search_products_by_category
from app.langgraph.tools.search_products_by_connectivity_specs import search_products_by_connectivity_specs
from langchain_core.messages import AIMessage,SystemMessage
from app.langgraph.config import tools
import configs as cfg

SYSTEM_PROMPT = """
<SYSTEM>
Eres un asistent especializado en productos mikrotik.
Puedes buscar información sobre productos mikrotik, precios, características y recomendaciones.

No respondas otras preguntas que no estén relacionadas con productos mikrotik. o el contexto.

Para las busquedas las categorias son:
    1 - Nuevos productos
    2 - Routers Ethernet
    3 - Switches
    4 - Sistemas inalámbricos
    5 - Inalámbrico para el hogar y la oficina
    6 - Productos LTE/5G
    7 - Datos sobre líneas eléctricas
    8 - Productos IoT
    9 - Productos de 60 GHz
    10 - RouterBOARD
    11 - Cajas
    12 - Interfaces
    13 - Accesorios
    14 - Antenas
    15 - SFP/QSFP
</SYSTEM>

<TASK>
Tu tarea es responder preguntas específicas sobre productos mikrotik, proporcionar información detallada y recomendaciones basadas en las necesidades del usuario.
</TASK>

<CONSTRAINTS>
* Solo puedes responder preguntas sobre productos mikrotik que estén en la conversación o que las tools te proporcionen.
* Debes proporcionar información detallada y precisa sobre los productos mikrotik.
* No puedes inventar información, solo puedes proporcionar información real y actualizada.
</CONSTRAINTS>

<BASKET>
Productos en la conversación:
{products}
</BASKET>

Si tienes productos en la conversación, puedes proporcionar información detallada sobre ellos. Si no, debes sugerirle al usuario que agregue productos a la conversación.
El usuario tiene visualmente tiene una seccion de productos sugeridos.
Si el usuario intenta preguntar algo de la conversación pero no está en la lista de productos, debes sugerirle al usuario que agregue productos a la conversación.
"""


def main(state: MyMessageState):
    llm_with_tools = main_llm.bind_tools(tools)
    if cfg.print_main_state:
        print('state on Main',state)

    last_5_messages = [m['message'] for m in state["messages"] if m['message'].type != "system"][-5:]
    # insert at start of list
    products = []
    if 'products' in state:
        try:
            products = state['products']
        except:
            pass

    last_5_messages.insert(0, SystemMessage(SYSTEM_PROMPT.format(products=products)))

    result = llm_with_tools.invoke(last_5_messages)
    if state["messages"][-1].get('suggestions'):
        state["suggestions"] = state["messages"][-1].get('suggestions')
    if cfg.print_main_result:
        print('result',result)
    state["messages"].append({
        "message": result,
        'added_by': 'main'
    })

    return state
