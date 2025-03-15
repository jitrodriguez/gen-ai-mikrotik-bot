from app.langgraph.config import main_llm
from typing import TypedDict
from pydantic import Field
from typing import Literal, TypedDict
from pydantic import Field
from app.langgraph.config import MyMessageState
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
import configs as cfg

agents = ["main_agent", "about_agent", "compare_agent"]

SYSTEM_PROMPT = (
    """Eres un trabajador en un equipo de trabajadores encargados de responder preguntas, eres un enrutador y tienes que decidir a qué trabajador enviar la pregunta a continuación.
Estos son los siguientes trabajadores: {agents},
* compare_agent: SOLO para preguntas que requieran comparaciones entre productos, marcas, modelos, precios, especificaciones técnicas, etc.
* main_agent: SOLO para preguntas específicamente sobre routers, telecomunicaciones, equipos de red y particularmente la marca mikrotik.
* about_agent: ESTRICTAMENTE LIMITADO a elementos conversacionales básicos (saludos formales como hola/hi/hola, despedidas como adiós/bye, agradecimientos, risas como 'jaja'/'hahaha') y preguntas directas sobre el bot mismo (nombre, propósito, capacidades, arquitectura del chat). Nada tecnico de telecomunicaciones.


RESTRICCIONES:
* Debes enrutar la pregunta al trabajador correcto basándote en el contenido de la pregunta y el contexto de la conversación.
* Debes proporcionar una explicación clara y concisa de por qué estás enrutando la pregunta a un trabajador específico.

EJEMPLO-1:
* Contexto: [
    Hola, tengo una pregunta sobre el router mikrotik, ¿puedes ayudarme?,
    Claro, ¿en qué necesitas ayuda?
]
* Pregunta: ¿Cuál es la diferencia entre el modelo A y el modelo B del router mikrotik?
* siguiente: main_agent
* pensamiento: La pregunta es sobre routers y una comparación entre dos modelos, por lo que debe ser enrutada al main_agent.

EJEMPLO-2:
* Contexto: [
    Hola, tengo una pregunta sobre el router mikrotik, ¿puedes ayudarme?,
    Claro, ¿en qué necesitas ayuda?
]
* Pregunta: ¿Cuál es tu nombre?
* siguiente: about_agent
* pensamiento: La pregunta es un elemento conversacional básico, por lo que debe ser enrutada al about_agent.

EJEMPLO-3:
* Contexto: [
    Hola, tengo una pregunta sobre el router mikrotik, ¿puedes ayudarme?,
    Claro, ¿en qué necesitas ayuda?,
    dame 2 switches baratos,
    claro, aquí hay 2 opciones: [switch1, switch2]
]
* Pregunta: ¿Cuál es mejor, switch1 o switch2?
* siguiente: main_agent
* pensamiento: La pregunta es sobre equipos de red, por lo que debe ser enrutada al main_agent.

EJEMPLO-4:
* Contexto: [
    Hola, tengo una pregunta sobre el router mikrotik, ¿puedes ayudarme?,
    Claro, ¿en qué necesitas ayuda?,
    dame 2 switches baratos,
    claro, aquí hay 2 opciones: [switch1, switch2]
]
* Pregunta: ¿Cómo estás?
* siguiente: about_agent
* pensamiento: La pregunta es un elemento conversacional básico, por lo que debe ser enrutada al about_agent.


EJEMPLO-6:
* Contexto: [
    Hola, tengo una pregunta sobre el router mikrotik, ¿puedes ayudarme?,
    Claro, ¿en qué necesitas ayuda?,
]
* Pregunta: ¿Cuál es el router más barato?
* siguiente: main_agent
* pensamiento: La pregunta es sobre routers y una comparación entre modelos, por lo que debe ser enrutada al main_agent.

EJEMPLO-7:
* Contexto: [
    Hola, tengo una pregunta sobre el router mikrotik, ¿puedes ayudarme?,
    Claro, ¿en qué necesitas ayuda?,
]
* Pregunta: Quiero saber que router es mejor, el modelo A o el modelo B
* siguiente: compare_agent
* pensamiento: La pregunta es sobre una comparación entre dos modelos, por lo que debe ser enrutada al compare_agent.

EJEMPLO-8:
* Contexto: [
    Existe el modelo A con x especificaciones y el modelo B con y especificaciones,
]
* Pregunta: ¿Cuál es mejor?
* siguiente: compare_agent
* pensamiento: La pregunta es sobre una comparación entre dos modelos, por lo que debe ser enrutada al compare_agent.


Contexto: {context}
    """)


class Router(TypedDict):
    """Worker to route to next"""
    next: Literal[*agents]
    think: str = Field(description="All thoughts to be shared with the next worker")

def router(state: MyMessageState):
    last_data = state["messages"][-1]
    last_message = last_data.get('message')
    if last_data.get('unreadable'):
        state["messages"].append(
            {
            'message': AIMessage("No he entendido, puedes reformular tu pregunta?"),
            'next': 'end',
            'added_by': 'router'
            }
        )
        return state
    llm_structured = main_llm.with_structured_output(Router,method= 'json_schema')
    if cfg.print_router_state:
        print('state on Router',state)
    # get last 5 messages that are not type SystemMessage
    # check if there is a type 'system'
    last_messages = [ m['message'] for m in state["messages"] if m['message'].type != "system" ][-5:]
    context = [m.content for m in last_messages]
    messages = [
        SystemMessage(SYSTEM_PROMPT.format(agents=agents,context=context)),
        HumanMessage(f"Pregunta:{last_message.content}")
    ]
    response = llm_structured.invoke(messages)
    # change las message
    last_data["next"] = response["next"]
    if cfg.print_next_think:
        print('think',response['think'])
    return state

def router_conditional_path(state:MyMessageState)->Literal["about","main","compare","__end__"]:
    last_message = state["messages"][-1]
    next_agent = last_message.get('next','end')
    if cfg.print_next:
        print('next_agent',next_agent)
    agents = {
        "main_agent": "main",
        "about_agent": "about",
        "compare_agent": "compare",
        "end": END
    }
    return agents.get(next_agent)