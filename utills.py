
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()
import os


# ========== Multi-user session memory ==========
USER_SESSIONS = {}   # { user_id: {pdf_path, qa_chain} }

api_key = os.getenv("GROQ_OPENAI_API_KEY")

def load_and_process_pdf(user_id: str, pdf_path: str):
    """
    Loads a PDF, chunks it, embeds it, and creates a QA chain for that user.
    """

    # 1. Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # 2. Split into chunks
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)

    # 3. Embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )

    # 4. Vector DB (created per user)
    vectordb = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=f"chroma_store/{user_id}"
    )

    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    # 5. LLM (Groq)
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        groq_api_key=api_key
    )

    # 6. Strict prompt
    prompt_template = """
    You are a helpful and polite assistant chatbot. Follow these rules:
    1. If the user greets you or asks something casual (like 'hello', 'hi', 'how are you?'), respond politely and conversationally.
    2. If the user expresses curiosity, confusion, or is testing you (like 'can you answer anything?' or 'are you limited?'), respond by explaining your purpose in a friendly way, for example:
    "I am specifically designed to answer questions based on the PDF content you provide. I can't answer questions outside of that, but I can help you with anything in the document!"
    3. If the user expresses that they are no longer interested in chatting (like 'I don’t want to chat', 'stop', 'no more questions'), respond politely and conclude the conversation in a friendly way, for example:
    "No worries! If you have questions later about the PDF, feel free to ask. Have a great day!"
    4. If the user asks a factual question related to the PDF, answer ONLY using the information provided in the PDF context below.
    5. If the question is not in the PDF, respond politely, acknowledging the user's request but clarifying the limitation:
    "It looks like the information you’re asking for isn’t in the PDF. Feel free to ask something that the document covers!"
    6. Do NOT use any knowledge outside the provided PDF context for informational questions.
    7. Always respond in a friendly, human-like manner, using proper grammar, sentences, and optionally some mild formatting like bold for emphasis.

    Context:
    {context}

    Question: {question}

    Answer:
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )

    # Save user session data
    USER_SESSIONS[user_id] = {
        "pdf_path": pdf_path,
        "qa_chain": qa_chain
    }


def get_user_chain(user_id: str):
    """
    Returns a user's QA chain if PDF is uploaded.
    """
    return USER_SESSIONS.get(user_id)
