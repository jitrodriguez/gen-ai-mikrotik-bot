from app.langgraph.config import MyMessageState
from langchain_core.messages import ToolMessage
import json
import configs as cfg

class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, state: MyMessageState):
        message = state["messages"][-1]['message']
        products = {}
        for tool_call in message.tool_calls:
            if cfg.print_tool_calls:
                print('tool_call name',tool_call["name"])
                print('tool_call args',tool_call["args"])
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            answer = tool_result['answer']
            tool_products = tool_result.get('suggestions', {})
            products = {**products, **tool_products}
            state["messages"].append(
                {
                   'message' :ToolMessage(
                    content=json.dumps(answer),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                    ),
                    'suggestions': tool_products
                }
            )
        return state