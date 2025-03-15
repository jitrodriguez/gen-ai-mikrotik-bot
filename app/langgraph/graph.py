from langgraph.graph.message import add_messages
from app.langgraph.config import MyMessageState
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from app.langgraph.agents.rephraser import rephraser
from app.langgraph.agents.router import router,router_conditional_path
from app.langgraph.agents.about import about
from app.langgraph.agents.main import main
from app.langgraph.agents.compare import compare, compare_conditional_path

from IPython.display import Image
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.checkpoint.memory import MemorySaver
from app.langgraph.config import tools
from langgraph.prebuilt import ToolNode
from app.langgraph.tools.main import BasicToolNode
from typing import Union, Literal


def tools_condition(
    state: MyMessageState
) -> Literal["tools", "__end__"]:
    ai_message = state["messages"][-1]["message"]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "__end__"


tool_node = BasicToolNode(tools=tools)

def get_graph():
    graph_builder = StateGraph(MyMessageState)

    # memory = MemorySaver()
    graph_builder.add_node("rephraser",rephraser)
    graph_builder.add_node("about",about)
    graph_builder.add_node("router",router)
    graph_builder.add_node("main",main)
    graph_builder.add_node("compare",compare)
    graph_builder.add_node("tools",tool_node)

    graph_builder.add_edge(START,"router")
    graph_builder.add_edge("rephraser","router")
    graph_builder.add_conditional_edges("router",router_conditional_path)
    graph_builder.add_conditional_edges("main",tools_condition)
    graph_builder.add_edge("tools","main")
    graph_builder.add_conditional_edges("compare",compare_conditional_path)
    graph_builder.add_edge("about",END)

    # graph = graph_builder.compile(checkpointer=memory)
    graph = graph_builder.compile()
    # print(graph.get_graph())
    # image = Image(
    #     graph.get_graph().draw_mermaid_png(
    #         draw_method=MermaidDrawMethod.API,
    #     )
    # )

    # # Guardar la imagen como un archivo PNG
    # with open("graph.png", "wb") as f:
    #     f.write(image.data)
    return graph