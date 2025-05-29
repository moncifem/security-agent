from utils.model import model
from tools import http_request
from langgraph.prebuilt import create_react_agent
from utils.checkpointer import shared_checkpointer


executor_agent = create_react_agent(
    model=model,
    name="executor_agent",
    tools=[http_request],
    prompt="""
    You are a security expert. You know how to find vulnerabilities in a swagger file.
    You will be given a plan of attacks and payloads.
    You must use the http_request tool to execute the attacks and payloads.
    You must also use the memory to store the results of your tests and payloads.
    
    MEMORY MANAGEMENT:
    - You can find the payloads to be used in the memory
    - Store all the results of your tests in the memory
    
    When you are done, check the memory that you have all the endpoints covered with tests.
    """,
    checkpointer=shared_checkpointer
)


if __name__ == "__main__":
    config = {
    "configurable": {
        "thread_id": "1"  
        }
    }
    executor_response = executor_agent.invoke(
        {"messages": [{"role": "user", "content": "Execute the attacks on the swagger file"}]},
        config
    )
    print(executor_response)