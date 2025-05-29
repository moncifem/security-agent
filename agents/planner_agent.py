from utils.model import model
from tools import get_swagger
from langgraph.prebuilt import create_react_agent
from utils.checkpointer import shared_checkpointer


planner_agent = create_react_agent(
    model=model,
    name="planner_agent",
    tools=[],
    prompt="""
    You are a security expert. You know how to find vulnerabilities in a swagger file.
    Your task is to plan all the possible attacks you can think of on the swagger file.
    Then you must generate all the payloads you can think of to exploit the vulnerabilities.
    Re iterate on your plan and payloads until you are sure you have covered all the possible vulnerabilities.
    
    MEMORY MANAGEMENT:
    - You can find the swagger to be used in the memory
    - Store all the payloads you generate in the memory
    - Store all the remarks you make in the memory
    
    When you are done, check the memory that you have all the swagger covered with tests.
    """,
    checkpointer=shared_checkpointer
)


if __name__ == "__main__":
    config = {
    "configurable": {
        "thread_id": "1"  
        }
    }
    planner_response = planner_agent.invoke(
        {"messages": [{"role": "user", "content": "Plan the attacks on the swagger file"}]},
        config
    )
    print(planner_response)