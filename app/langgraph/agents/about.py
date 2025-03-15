from app.langgraph.config import main_llm
from app.langgraph.config import MyMessageState
from langchain_core.messages import SystemMessage, AIMessage
import configs as cfg

SYSTEM_PROMPT = """
<PERSONA>
Eres un asistente que ayuda a responder preguntas de los usuarios.
Específicamente tú respondes preguntas del siguiente texto, solo response lo que el usuario pregunte, no des información extra:
</PERSONA>
<CONSTRAINTS>

* Te llamas mikrotik bot
* Fuiste creado para responder preguntas sobre routers, equipos de telecomunicaciones y en particular la marca mikrotik.
* Siempre debes responder de manera clara y precisa, evitando respuestas ambiguas o incorrectas.
* Siempre debes responder con información actualizada y relevante.
* Te crearon en un curso de IA Donde se trabajó con langchain y langgraph.
* Tu creador es Juan Rodriguez. Desarrollador de software y entusiasta por el desarrollo de IA.

</CONSTRAINTS>
"""

def about(state: MyMessageState):
    last_5_messages = [ m['message'] for m in state["messages"] if m['message'].type != "system" ][-5:]
    if cfg.print_about_state:
        print('state on About',state)
    messages = [
        SystemMessage(SYSTEM_PROMPT),
        *last_5_messages
    ]
    response = main_llm.invoke(messages)
    state["messages"].append(
        {
            'message': AIMessage(response.content),
            'added_by': 'about'
        }
    )
    return state