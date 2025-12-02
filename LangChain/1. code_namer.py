import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# --- 1. & 2. Define the LLM ---
# API Key is expected in the GEMINI_API_KEY environment variable.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", # A fast and cost-effective model
    temperature=0.7
)

# --- 3. Define the Prompt Template ---
template = """
You are an expert Python developer and a master of naming conventions.
Your task is to suggest 5 concise, clear, and Pythonic names 
(snake_case for functions, PascalCase for classes) for the following code description. 
Return only the 5 names, each on a new line, with no extra text or numbering.

Code Description: {description}
"""

prompt = PromptTemplate(
    input_variables=["description"],
    template=template,
)

# --- 4. Build the Chain using LCEL ---
# This is the modern and correct way to chain a Prompt and an LLM.
name_chain = prompt | llm

# --- 5. Run and Test ---
description_input = "A function that reads a CSV file, filters rows where the 'status' column is 'active', and returns the resulting dataframe."

print(f"--- Description ---\n{description_input}\n-------------------")

# Run the chain using .invoke() and access the content
response = name_chain.invoke({"description": description_input})

print("Suggested Pythonic Names:\n")
# The response from a ChatModel (llm) is a ChatMessage object.
# We extract the string content using the .content attribute.
print(response.content)