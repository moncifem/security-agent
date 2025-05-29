from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

model = ChatAnthropic(model="claude-3-5-sonnet-latest")

if __name__ == "__main__":
    print(model.invoke("Hello, world!").content)
