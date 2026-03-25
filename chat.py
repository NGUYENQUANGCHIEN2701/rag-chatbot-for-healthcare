from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_store = FAISS.load_local(
    "./db/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 5,
        "score_threshold": 0.2
    }
)

def format_docs(docs):
    formatted = []
    for doc in docs:
        source = doc.metadata.get("source", "Không rõ nguồn")
        page = doc.metadata.get("page", "Không rõ trang")
        content = doc.page_content
        formatted.append(f"Nguồn: {source}, Trang: {page}\nNội dung: {content}")
    return "\n\n".join(formatted)

template = (
    "Bạn là trợ lý tra cứu sơ cấp cứu cho một kho tri thức nội bộ. "
    "Bạn chỉ được trả lời dựa trên tài liệu được cung cấp.\n\n"
    "NGUYÊN TẮC:\n"
    "1) Chỉ sử dụng ngữ cảnh được cung cấp để trả lời.\n"
    "2) Nếu câu trả lời không có rõ trong tài liệu, hãy trả lời đúng nguyên văn: "
    "\"Tôi không biết dựa trên các tài liệu đã cung cấp.\"\n"
    "3) Không dùng kiến thức bên ngoài, không đoán, không bịa.\n"
    "4) Trả lời hoàn toàn bằng tiếng Việt.\n"
    "5) Nếu phù hợp, trích dẫn nguồn theo dạng (source:page).\n\n"
    "Ngữ cảnh:\n{context}\n\n"
    "Câu hỏi: {question}"
)

prompt = ChatPromptTemplate.from_template(template)

llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0.0
)

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

while True:
    question = input("\nCâu hỏi (gõ 'exit' để thoát): ")
    if question.lower() in ["exit", "quit", "q"]:
        break

    answer = rag_chain.invoke(question)
    print("\nCâu trả lời:\n")
    print(answer)