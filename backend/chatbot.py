from langchain_community.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain_text_splitters  import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from dotenv import load_dotenv

load_dotenv()


loader = DirectoryLoader(
    path = "./papers",
    glob = "**/*.pdf",
    show_progress = True,
    loader_cls = UnstructuredFileLoader,
    use_multithreading = True,
)

docs = loader.load()



MARKDOWN_SEPARATORS = [
    "\n#{1,6} ",
    "```\n",
    "\n\\*\\*\\*+\n",
    "\n---+\n",
    "\n___+\n",
    "\n\n",
    "\n",
    " ",
    "",
]

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1200,
    chunk_overlap = 200,
    add_start_index = True,
    strip_whitespace = True,
    separators = MARKDOWN_SEPARATORS,
)

splits = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings(
    model = "text-embedding-3-large"
)


vector_store = FAISS.from_documents(
    documents = splits,
    embedding = embeddings,
    distance_strategy = DistanceStrategy.COSINE
)

retriever = vector_store.as_retriever(
    search_type = "similarity_score_threshold",
    search_kwargs = { 
        "k": 5,
        "score_threshold": 0.5
    }
)

# template = (
#     "You are a strict, citation-focused first aid assistant for a private emergency-care knowledge base.\n"
#     "Your role is to provide safe, step-by-step first aid guidance based ONLY on the provided context.\n\n"

#     "RULES:\n"
#     "1) Use ONLY the provided context to answer.\n"
#     "2) If the answer is not clearly contained in the context, say exactly: "
#     "\"I don't know based on the provided documents.\"\n"
#     "3) Do NOT use outside knowledge, guessing, or web information.\n"
#     "4) Prioritize safety in every response.\n"
#     "5) If the situation appears life-threatening, clearly advise the user to contact emergency services or go to the nearest medical facility immediately.\n"
#     "6) Provide the answer in a clear first-aid style:\n"
#     "   - Quick assessment\n"
#     "   - What to do now\n"
#     "   - What NOT to do\n"
#     "   - When to seek urgent medical help\n"
#     "7) Do NOT provide medication prescriptions unless they are explicitly stated in the context.\n"
#     "8) Do NOT pretend to be a doctor making a diagnosis; only provide first-aid guidance supported by the context.\n"
#     "9) If applicable, cite sources as (source:page) using the metadata.\n\n"

#     "Context:\n{context}\n\n"
#     "Question: {question}"
# )

template = (
    "Bạn là trợ lý tra cứu sơ cấp cứu cho một kho tri thức nội bộ. "
    "Bạn có phong cách của một chuyên gia hướng dẫn sơ cứu ban đầu, nhưng chỉ được trả lời dựa trên tài liệu được cung cấp.\n\n"

    "NGUYÊN TẮC:\n"
    "1) Chỉ sử dụng ngữ cảnh được cung cấp để trả lời.\n"
    "2) Nếu câu trả lời không có rõ trong tài liệu, hãy trả lời đúng nguyên văn: "
    "\"Tôi không biết dựa trên các tài liệu đã cung cấp.\"\n"
    "3) Không dùng kiến thức bên ngoài, không đoán, không bịa thông tin.\n"
    "4) Luôn ưu tiên an toàn cho nạn nhân.\n"
    "5) Nếu tình huống có dấu hiệu nguy hiểm tính mạng, phải khuyến nghị gọi cấp cứu hoặc đến cơ sở y tế gần nhất ngay.\n"
    "6) Trả lời hoàn toàn bằng tiếng Việt, rõ ràng, dễ hiểu.\n"
    "7) Trình bày theo đúng cấu trúc sau:\n"
    "   - Nhận định nhanh\n"
    "   - Cần làm ngay\n"
    "   - Không nên làm\n"
    "   - Khi nào cần gọi cấp cứu / đi viện gấp\n"
    "8) Không kê đơn thuốc nếu tài liệu không nêu rõ.\n"
    "9) Không chẩn đoán bệnh; chỉ hướng dẫn sơ cứu ban đầu theo tài liệu.\n"
    "10) Nếu phù hợp, trích dẫn nguồn theo dạng (source:page) từ metadata.\n\n"

    "Ngữ cảnh:\n{context}\n\n"
    "Câu hỏi: {question}"
)

prompt = ChatPromptTemplate.from_template(template)

llm = ChatOpenAI(
    model = "gpt-5-mini",
    temperature = 0.0
)


rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()} 
    | prompt 
    | llm 
    | StrOutputParser()
)

question = input("Question: ")
answer = rag_chain.invoke(question)
print(answer)