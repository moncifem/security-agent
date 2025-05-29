from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

model = ChatAnthropic(model="claude-3-7-sonnet-latest", temperature=0.8)

if __name__ == "__main__":
    print(model.invoke("Hello, world!").content)
