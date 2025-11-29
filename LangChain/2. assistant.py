import os

# Modern Imports for LLM, Embeddings, Core Components
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Document Handling Imports
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter  # Installed via pip install langchain-text-splitters
from langchain_community.vectorstores import FAISS

# NOTE: The following memory import and logic has been removed to resolve dependency issues:
# from langchain.memory import ConversationBufferMemory

# --- 1. SETUP ---
# Ensure GOOGLE_API_KEY or GEMINI_API_KEY is set in PyCharm's Run Configuration
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    # If the environment variable isn't found, this will raise an error immediately.
    raise ValueError("API Key not found. Please set GOOGLE_API_KEY or GEMINI_API_KEY.")

# --- 2. DATA PREPARATION (RAG) ---

# A. Load Document
# Ensure you have a 'knowledge.txt' file in the same directory.
try:
    loader = TextLoader("C:\\Users\gamer\PycharmProjects\Side-projects\LangChain\Files_for_testing\\2. knowledge.txt")
    documents = loader.load()
except FileNotFoundError:
    print("WARNING: knowledge.txt not found. Please create it or change the file path.")
    # Use a dummy document to prevent crash if file is missing
    documents = []

# B. Split Text (for efficient retrieval)
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

# C. Create Embeddings and Vector Store
# We use a Gemini embedding model for generating dense vectors from the text.
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=api_key)
vectorstore = FAISS.from_documents(docs, embeddings)

# Create a retriever component to fetch relevant documents
retriever = vectorstore.as_retriever()

# --- 3. PROMPT AND LLM SETUP ---

# A. Define the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    google_api_key=api_key
)

# B. Define the Stateless Prompt
# The prompt now ONLY accepts context and question.
template = """
You are a helpful Research Assistant. Answer the user's question based ONLY on the provided context.
If the answer is not in the context, politely state that you do not have enough information.

--- CONTEXT ---
{context}

--- QUESTION ---
{question}
"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", template),
        ("human", "{question}")
    ]
)


# --- 4. BUILD THE FINAL CHAIN (LCEL) ---

# Function to format the retrieved documents into a single string for the prompt
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# The RAG chain pipeline:
# 1. Take input {"question": "..."}
# 2. Use RunnablePassthrough.assign to call the retriever and fetch context
# 3. Pass context and question to the prompt
# 4. Pass the resulting message to the LLM
rag_chain = (
        RunnablePassthrough.assign(context=(lambda x: x["question"]) | retriever | format_docs)
        | prompt
        | llm
)

# --- 5. EXECUTE THE CONVERSATION ---

print("🤖 Research Assistant Initialized. (Stateless Mode)")
print("Ask about your knowledge.txt content.")
print("Type 'quit' or 'exit' to end the session.")
print("-" * 30)

while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        break

    # 1. Get the answer using the RAG chain
    # We only invoke the chain with the 'question' input now.
    response = rag_chain.invoke({"question": user_input})

    # 2. Print the answer
    print(f"Assistant: {response.content}")

    # Note: No memory saving/updating is performed here.