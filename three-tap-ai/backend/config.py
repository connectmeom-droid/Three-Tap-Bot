import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Create the AI model instance here
# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     api_key=GROQ_API_KEY
# )
