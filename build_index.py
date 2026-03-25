from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

loader = DirectoryLoader(
    path="./papers",
    glob="**/*.pdf",
    show_progress=True,
    loader_cls=PyPDFLoader,
    use_multithreading=True,
)

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    add_start_index=True,
    strip_whitespace=True,
)

splits = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_store = FAISS.from_documents(
    documents=splits,
    embedding=embeddings,
    distance_strategy=DistanceStrategy.COSINE
)

vector_store.save_local("./db/faiss_index")

print("Da build va luu FAISS index vao ./db/faiss_index")