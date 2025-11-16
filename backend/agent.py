from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from hr_assist import TOOLS, TOOL_FUNCTIONS

class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]

class HRAssistAgent:
    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("llm", self._call_llm)
        graph.add_node("tools", self._call_tool)
        graph.add_edge("tools", "llm")
        graph.add_conditional_edges("llm", self._should_continue, {"continue": "tools", "end": END})
        graph.set_entry_point("llm")
        return graph.compile()

    def _should_continue(self, state: AgentState):
        messages = state['messages']
        last_message = messages[-1]
        if not last_message.tool_calls:
            return "end"
        else:
            return "continue"

    def _call_llm(self, state: AgentState):
        messages = state['messages']
        model = ChatOpenAI(model="gpt-4")
        response = model.invoke(messages)
        return {"messages": [response]}

    def _call_tool(self, state: AgentState):
        messages = state['messages']
        last_message = messages[-1]
        tool_call = last_message.tool_calls[0]
        tool_name = tool_call['name']
        tool_args = tool_call['args']

        if tool_name in TOOL_FUNCTIONS:
            response = TOOL_FUNCTIONS[tool_name](**tool_args)
            return {"messages": [ToolMessage(content=str(response), tool_call_id=tool_call['id'])]}
        else:
            return {"messages": [ToolMessage(content=f"Tool {tool_name} not found", tool_call_id=tool_call['id'])]}

    def chat(self, user_message: str, authenticated_user_id: str, user_name: str = None):
        system_message = SystemMessage(content="You are a helpful HR assistant.")

        context_prefix = f"[Authenticated User: {authenticated_user_id}"
        if user_name:
            context_prefix += f", Name: {user_name}"
        context_prefix += "] "

        contextual_message = context_prefix + user_message
        user_message = HumanMessage(content=contextual_message)

        initial_state = {"messages": [system_message, user_message]}
        response = self.graph.invoke(initial_state)
        return response['messages'][-1].content
