from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

import os

os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_KEY"
os.environ["SERPAPI_API_KEY"] = "YOUR_SERPAPI_KEY"

# --- Gemini LLM ---
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.2,
)

# --- Tools ---
search = SerpAPIWrapper()
search_tool = Tool(
    name="web_search",
    func=search.run,
    description="Search the web."
)

def scrape_url(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs[0].page_content

scraper_tool = Tool(
    name="scrape_webpage",
    func=scrape_url,
    description="Extract raw text from a webpage URL."
)

# --- Agent ---
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=[search_tool, scraper_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=memory
)

# --- Run agent ---
query = "Research the solar panel market in Pakistan 2024, competitors, prices, and trends."
response = agent.run(query)

print("\n\nFinal Research Report:\n")
print(response)