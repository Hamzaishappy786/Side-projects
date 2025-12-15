import os
import sys
from dotenv import load_dotenv

# LangChain Imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# Load environment variables (Make sure you have GOOGLE_API_KEY in a .env file)
load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATA_FOLDER = "data"
DB_PERSIST_DIR = "vector_db"


def create_vector_db():
    """
    1. Loads PDF data
    2. Splits it into chunks
    3. Embeds it using Gemini
    4. Saves it to a local Vector Database (Chroma)
    """
    # Check if data folder exists
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print(f"⚠️  Folder '{DATA_FOLDER}' created. Please put a PDF file inside it and run this script again.")
        return None

    pdf_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.pdf')]
    if not pdf_files:
        print(f"⚠️  No PDF found in '{DATA_FOLDER}'. Please add one.")
        return None

    print("📄 Loading PDF...")
    # Load the first PDF found in the data folder
    loader = PyPDFLoader(os.path.join(DATA_FOLDER, pdf_files[0]))
    documents = loader.load()

    print("✂️  Splitting text...")
    # Split text into manageable chunks (overlap helps maintain context)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    print("💾 Creating Embeddings and Vector Store...")
    # Use Gemini's embedding model
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Create the vector store
    vectordb = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=DB_PERSIST_DIR
    )
    print("✅ Vector Database created successfully!")
    return vectordb


def load_vector_db():
    """Loads the existing Vector DB if it was already created"""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectordb = Chroma(persist_directory=DB_PERSIST_DIR, embedding_function=embeddings)
    return vectordb


def start_chat_interface(qa_chain):
    """Simple CLI Loop for chatting"""
    print("\n🤖 RAG Chatbot is Ready! (Type 'exit' to quit)")
    print("-" * 50)

    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            break

        try:
            # The chain retrieves context and generates an answer
            response = qa_chain.invoke({"query": query})
            print(f"AI: {response['result']}")

            # Optional: Print sources to show where the info came from
            # print(f"\n[Source: Page {response['source_documents'][0].metadata['page']}]")
            print("-" * 50)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Check if we need to build the DB or just load it
    if not os.path.exists(DB_PERSIST_DIR):
        print("Initializing Database for the first time...")
        vectordb = create_vector_db()
    else:
        print("Loading existing Database...")
        vectordb = load_vector_db()

    if vectordb:
        # Initialize the Gemini Chat Model
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

        # Create the Retrieval Chain
        # "stuff" chain type simply stuffs the retrieved context into the prompt
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectordb.as_retriever(search_kwargs={"k": 3}),  # Retrieve top 3 relevant chunks
            return_source_documents=True
        )

        start_chat_interface(qa_chain)