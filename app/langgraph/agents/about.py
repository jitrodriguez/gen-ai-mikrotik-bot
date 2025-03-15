from app.langgraph.config import main_llm
from app.langgraph.config import MyMessageState
from langchain_core.messages import SystemMessage, AIMessage
import configs as cfg
from app.langgraph.tools.get_bot_info import get_bot_info

SYSTEM_PROMPT = """
<PERSONA>
Eres un asistente que ayuda a responder preguntas de los usuarios.
Siempre responde con en primera persona.
</PERSONA>
<CONSTRAINTS>
* Llama a las tools si necesitas información extra.
* En saludos y despedidas, responde de manera amigable y no es necesario que llames a las tools.
* Para la llama a la herramienta de información del bot recuerda dar una query que sea para una base de datos vectorial.
</CONSTRAINTS>
<EJEMPLOS-1>
- ¿Quien eres?
- ¿Qué haces?
- ¿Cuál es tu función?
</EJEMPLOS-1>
En caso el usuario se salga del tema, responder con:
    Solo puedo responder preguntas relacionadas con la información que tengo.

"""

def about(state: MyMessageState):
    last_5_messages = [ m['message'] for m in state["messages"] if m['message'].type != "system" ][-5:]
    if cfg.print_about_state:
        print('state on About',state)
    messages = [
        SystemMessage(SYSTEM_PROMPT),
        *last_5_messages
    ]
    llm_with_tools = main_llm.bind_tools([get_bot_info])
    response = llm_with_tools.invoke(messages)
    state["messages"].append(
        {
            'message': response,
            'added_by': 'about'
        }
    )
    if cfg.print_about_response:
        print('response',response)
    return state