from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from prompt_library.prompt import SYSTEM_PROMPT
from tools.currency_conversion_tool import CurrencyConverterTool
from tools.expense_calculator_tool import CalculatorTool
from tools.place_search_tool import PlaceSearchTool
from tools.weather_info_tool import WeatherInfoTool
from utils.model_loader import ModelLoader


class GraphBuilder:
    def __init__(self, model_provider: str = "groq"):
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()

        self.weather_tools = WeatherInfoTool()
        self.place_search_tools = PlaceSearchTool()
        self.calculator_tools = CalculatorTool()
        self.currency_converter_tools = CurrencyConverterTool()

        self.tools = [
            *self.weather_tools.weather_tool_list,
            *self.place_search_tools.place_search_tool_list,
            *self.calculator_tools.calculator_tool_list,
            *self.currency_converter_tools.currency_converter_tool_list,
        ]

        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        self.graph = None
        self.system_prompt = SYSTEM_PROMPT

    def agent_function(self, state: MessagesState):
        """Invoke the LLM with system instructions and conversation history."""
        input_question = [self.system_prompt] + state["messages"]
        response = self.llm_with_tools.invoke(input_question)
        return {"messages": [response]}

    def build_graph(self):
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools, handle_tool_errors=True))
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")
        self.graph = graph_builder.compile()
        return self.graph

    def __call__(self):
        return self.build_graph()
