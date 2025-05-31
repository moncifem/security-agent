# imports
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from typing import TypedDict, List, Optional
import json
import logging
from utils import model
from tools.swagger_tool import get_swagger

logger = logging.getLogger(__name__)


# Define graph state
class StateAnnotation(TypedDict):
    input: BaseMessage
    swagger_json: dict
    scenarios: list[str]
    output: str


# Define nodes

# 1. swagger node - transform a url to a swagger_json
def swagger_node(state: StateAnnotation) -> StateAnnotation:
    logger.info("[SwaggerNode]: Processing input")
    # get the user query
    user_query = str(state["input"].content)
    logger.info(f"[SwaggerNode]: User query: {user_query}")
    
    system_prompt = """
    You are an OpenAPI/Swagger analyst. Your task is to:
    1. Extract the URL from the user's message
    2. Use the get_swagger tool to fetch the Swagger/OpenAPI specification
    3. Return the complete swagger data for further processing
    
    The user will provide a URL to a swagger/openapi specification.
    Call the get_swagger tool with the extracted URL.
    """
    
    # Bind the tool to the model
    model_with_tools = model.bind_tools([get_swagger])
    
    # Create messages
    messages = [
        ("system", system_prompt),
        ("human", user_query)
    ]
    
    # Invoke model with tools
    response = model_with_tools.invoke(messages)
    
    # Process tool calls
    if response.additional_kwargs.get("tool_calls"):
        tool_result = json.loads(response.additional_kwargs["tool_calls"][0]["function"]["arguments"])
        logger.info("[SwaggerNode]: Successfully retrieved swagger JSON")
        logger.info(f"[SwaggerNode] Output: {json.dumps(tool_result, indent=2)}")
        return {"swagger_json": tool_result}
    else:
        # Fallback: try to extract URL directly and call tool
        # This handles cases where the model doesn't use the tool
        url = user_query.strip()
        if url.startswith(("http://", "https://")):
            tool_result = get_swagger.invoke({"url": url})
            if tool_result.get("success"):
                logger.info("[SwaggerNode]: Successfully retrieved swagger JSON")
                logger.info(f"[SwaggerNode] Output: {json.dumps(tool_result['data'], indent=2)}")
                return {"swagger_json": tool_result["data"]}
            else:
                # Handle error case
                error_msg = tool_result.get("error", "Unknown error")
                logger.error(f"[SwaggerNode]: Failed to retrieve swagger JSON - {error_msg}")
                return {"swagger_json": {"error": error_msg}}
    # Fallback: try to extract URL directly and call tool
    # This handles cases where the model doesn't use the tool
    url = user_query.strip()
    if url.startswith(("http://", "https://")):
        tool_result = get_swagger.invoke({"url": url})
        if tool_result.get("success"):
            return {"swagger_json": tool_result["data"]}
        else:
            return {"swagger_json": {"error": tool_result.get("error", "Failed to fetch swagger")}}
    
    return {"swagger_json": {"error": "No valid URL found in input"}}

# 2. planner node - plan the scenarios
def planner_node(state: StateAnnotation) -> StateAnnotation:
    logger.info("[PlannerNode]: Starting scenario planning")
    # get the swagger_json
    # swagger_json = str(state["swagger_json"].content)
    
    # system_prompt = """ """
    
    # # create a structured model
    # structured_model = model.with_structured_output(json) # TODO: add a structured output model
    
    # # create messages
    # messages = [
    #     ("system", system_prompt),
    #     ("human", swagger_json)
    # ]
    
    # response = structured_model.invoke(messages)
    
    # return {"scenarios": response}
    # For now, return an empty list of scenarios
    return {"scenarios": []}
    
    
# 3. executor node - execute the scenarios
def executor_node(state: StateAnnotation) -> StateAnnotation:
    logger.info("[ExecutorNode]: Starting scenario execution")
    # get the scenarios
    # scenarios = state["scenarios"]
    
    # system_prompt = """ """
    
    # # create a structured model
    # structured_model = model.with_structured_output(json) # TODO: add a structured output model
    
    # # create messages
    # messages = [
    #     ("system", system_prompt),
    #     ("human", scenarios)
    # ]
    
    # response = structured_model.invoke(messages)
    
    # return {"output": response}
    return {"output": []}
    
    
# Compile the graph
def create_graph():
    logger.info("[Graph]: Initializing StateGraph")
    # Initialize the StateGraph
    graph = StateGraph(StateAnnotation)
    
    # Add nodes
    graph.add_node("swagger", swagger_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    
    # Add edges to define the flow
    graph.add_edge(START, "swagger")      # Start with swagger node
    graph.add_edge("swagger", "planner")  # swagger -> planner
    graph.add_edge("planner", "executor") # planner -> executor
    graph.add_edge("executor", END)       # executor -> end
    
    # Compile the graph
    logger.info("[Graph]: Compiling graph")
    compiled_graph = graph.compile()
    logger.info("[Graph]: Graph compilation complete")
    return compiled_graph

# Create the compiled graph
app = create_graph()

# Optional: To run the graph
# result = app.invoke({"input": your_base_message_here})

