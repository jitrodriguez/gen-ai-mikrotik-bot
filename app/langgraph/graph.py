from langgraph.graph.message import add_messages
from app.langgraph.config import MyMessageState
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from app.langgraph.agents.rephraser import rephraser
from app.langgraph.agents.router import router,router_conditional_path
from app.langgraph.agents.about import about
from app.langgraph.agents.main import main
from app.langgraph.agents.compare import compare, compare_conditional_path

# from IPython.display import Image
from langgraph.checkpoint.memory import MemorySaver
from app.langgraph.config import tools
from langgraph.prebuilt import ToolNode
from app.langgraph.tools.main import BasicToolNode
from typing import Union, Literal
from app.langgraph.tools.get_bot_info import get_bot_info
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles



def tools_condition(
    state: MyMessageState
) -> Literal["tools", "__end__"]:
    ai_message = state["messages"][-1]["message"]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "__end__"

def tools_about_condition(
    state: MyMessageState
) -> Literal["tools_about", "__end__"]:
    ai_message = state["messages"][-1]["message"]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools_about"
    return "__end__"


tool_node = BasicToolNode(tools=tools)
tool_node_about = BasicToolNode(tools=[get_bot_info])

def get_graph():
    graph_builder = StateGraph(MyMessageState)

    # memory = MemorySaver()
    # graph_builder.add_node("rephraser",rephraser)
    graph_builder.add_node("router",router)
    graph_builder.add_node("about",about)
    graph_builder.add_node("main",main)
    graph_builder.add_node("compare",compare)
    graph_builder.add_node("tools",tool_node)
    graph_builder.add_node("tools_about",tool_node_about)

    graph_builder.add_edge(START,"router")
    # graph_builder.add_edge("rephraser","router")
    graph_builder.add_conditional_edges("router",router_conditional_path)
    graph_builder.add_conditional_edges("main",tools_condition)
    graph_builder.add_edge("tools","main")
    graph_builder.add_conditional_edges("compare",compare_conditional_path)
    graph_builder.add_edge("tools_about","about")
    graph_builder.add_conditional_edges("about",tools_about_condition)

    # graph = graph_builder.compile(checkpointer=memory)
    graph = graph_builder.compile()
    # print(graph.get_graph())
    # image = Image(
    #     graph.get_graph().draw_mermaid_png(
    #         curve_style=CurveStyle.LINEAR,
    #         node_colors=NodeStyles(first="#ffdfba", last="#baffc9", default="#fad7de"),
    #         wrap_label_n_words=9,
    #         output_file_path=None,
    #         draw_method=MermaidDrawMethod.PYPPETEER,
    #         background_color="white",
    #         padding=10,
    #     )
    # )

    # Guardar la imagen como un archivo PNG
    # with open("graph.png", "wb") as f:
    #     f.write(image.data)
    return graph