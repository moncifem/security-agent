from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from utils.model import model
from agents import swagger_agent
from utils.checkpointer import shared_checkpointer


security_agent = create_supervisor(
    [swagger_agent],
    model=model,
    prompt="You are a security expert. Always use one tool at a time."
).compile(name="security_agent", checkpointer=shared_checkpointer)


if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "1"  
        }   
    }
    security_response = security_agent.invoke(
        {"messages": [{"role": "user", "content": "get the swagger from http://localhost:8000/openapi.json"}]},
        config
    )
    print(security_response)