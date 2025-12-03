from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
import pandas as pd
import os

# 1. A simple tool: filter CSV file
def filter_active_rows(file_path: str) -> str:
    df = pd.read_csv(file_path)
    filtered = df[df['status'] == 'active']
    return filtered.to_string(index=False)

filter_tool = Tool(
    name="filter_csv_status_active",
    func=filter_active_rows,
    description="Filters active rows from a CSV file based on 'status' column."
)

# 2. Setup Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY")
).bind_tools([filter_tool])  # ← Move here!

# 3. Setup prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a smart assistant. Decide if user request requires calling a tool."),
    ("human", "{input}")
])

# 4. LangChain runnable with tools
chain = prompt | llm

# 5. Test it
CSV_PATH = r"C:\Users\gamer\PycharmProjects\Side-projects\LangChain\Files_for_testing\3. data.csv"

# 5. Test it
user_query = f"Please filter the CSV located at '{CSV_PATH}' and show only active rows."
result = chain.invoke({"input": user_query})
print(result)