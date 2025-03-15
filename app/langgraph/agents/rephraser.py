from app.langgraph.config import main_llm
from typing import TypedDict
from pydantic import Field
from app.langgraph.config import MyMessageState
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
import configs as cfg

SYSTEM_PROMPT = """
<PERSONA>
Eres un asistente que ayuda a mejorar y reformular las solicitudes de los usuarios.
</PERSONA>

<TASK>
Tu tarea es SOLO reformular lo que el usuario ha escrito, manteniendo el mismo significado e intención pero mejorando su claridad y corrección gramatical.
</TASK>


<EXAMPLE-1>
{
original: "que es un router",
rephrased: "¿Qué es un router?",
unreadable: false
}
</EXAMPLE-1>

<EXAMPLE-2>
{
original: "Hola"
rephrased: "¡Hola! Buen día."
unreadable: false
}
</EXAMPLE-2>

<EXAMPLE-3>
{
original: "quiero saber precio router",
rephrased: "Me gustaría conocer el precio del router, por favor.",
unreadable: false
}
</EXAMPLE-3>
<EXAMPLE-4>
{
original: "Hey"
rephrased: "¡Hola!"
unreadable: false
}
</EXAMPLE-4>

<NEVER>
Original: "¿Cuál es el precio de un router?"
Reformulado: "El precio de un router es de $100."
</NEVER>

<NEVER>
Original: "Hola, ¿cómo estás?"
Reformulado: "Estoy bien, gracias."
</NEVER>

<CONSTRAINTS>
REGLAS ESTRICTAS:
1. MANTÉN SIEMPRE la misma intención comunicativa y propósito del mensaje original.
2. NUNCA cambies el tipo de mensaje (afirmación, pregunta, saludo, etc.).
3. NUNCA cambies una afirmación por una pregunta o viceversa.
4. NUNCA cambies el sujeto ni el objeto de la frase.
5. NO respondas a la pregunta, solo reformúlala.
6. NO cambies la solicitud por una respuesta.
7. NO agregues información nueva que no esté implícita en el mensaje original.
8. NO agregues ni quites información sustancial.
9. Solo mejora la gramática, ortografía, puntuación y fluidez.
</CONSTRAINTS>

"""


class Rephraser(TypedDict):
    """Worker to rephrase the user's request"""
    original: str = Field(description="Original request from the user, don't change this")
    rephrased: str = Field(description="Rephrased request from the user, correcting grammar, improving semantics, and enhancing clarity")
    unreadable: bool = Field(description="True if the rephrased request is unreadable")
    reason: str = Field(description="Reason why the rephrased request is unreadable, otherwise empty")

def rephraser(state: MyMessageState):
    llm_structured = main_llm.with_structured_output(Rephraser,method= 'json_schema')
    if cfg.print_rephraser_state:
        print('state on Rephraser',state)
    last_message = state["messages"][-1]["message"]
    # print('last_message',last_message.get('content'))
    messages = [
        SystemMessage(SYSTEM_PROMPT),
        HumanMessage(f"<QUESTION>{last_message.content}</QUESTION>"),
    ]
    response = llm_structured.invoke(messages)
    # change las message
    new_message = {
        'message': HumanMessage(response["rephrased"]) if not response["unreadable"] else last_message,
        'unreadable': response["unreadable"],
        'added_by': 'rephraser'
    }
    if cfg.print_rephrased_message:
        print('new_message',new_message)
    # delete last message from state
    state["messages"].pop()
    state["messages"].append(new_message)
    return state