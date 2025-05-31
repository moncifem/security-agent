import logging
from langchain_core.messages import HumanMessage
from graph import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test URL - you can replace this with any valid Swagger/OpenAPI URL
test_url = "https://petstore.swagger.io/v2/swagger.json"

# Create input message
input_message = HumanMessage(content=test_url)

# Run the graph
print("\nRunning graph with test URL:", test_url)
result = app.invoke({"input": input_message})

print("\nResult:", result)
