from utils.model import model
from tools import get_swagger
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver


swagger_agent = create_react_agent(
    model=model,
    tools=[get_swagger],
    name="swagger_agent",
    prompt="You are a swagger expert. Always use one tool at a time.",
    checkpointer=InMemorySaver()
)


if __name__ == "__main__":
    config = {
    "configurable": {
        "thread_id": "1"  
        }
    }
    swagger_response = swagger_agent.invoke(
        {"messages": [{"role": "user", "content": "get the swagger from http://localhost:8000/openapi.json"}]},
        config
    )
    print(swagger_response)