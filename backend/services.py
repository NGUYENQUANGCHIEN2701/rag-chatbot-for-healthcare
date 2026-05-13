import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

class ChatService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large"
        )
        
        # Load FAISS index
        self.vector_store = FAISS.load_local(
            "./db/faiss_index",
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 5,
                "score_threshold": 0.2
            }
        )
        
        template = (
            "Bạn là trợ lý tra cứu sơ cấp cứu cho một kho tri thức nội bộ. "
            "Nếu người dùng chỉ chào hỏi, cảm ơn hoặc giao tiếp thông thường (ví dụ: 'hello', 'chào bạn', 'bạn là ai'), hãy trả lời một cách tự nhiên, thân thiện và linh hoạt.\n"
            "Tuy nhiên, nếu người dùng hỏi về các vấn đề chuyên môn y tế, sơ cấp cứu, bệnh lý, BẠN PHẢI tuân thủ tuyệt đối các NGUYÊN TẮC sau:\n\n"
            "NGUYÊN TẮC Y TẾ:\n"
            "1) Chỉ sử dụng ngữ cảnh (context) được cung cấp để trả lời các câu hỏi y tế.\n"
            "2) Nếu thông tin y tế không có trong tài liệu (ví dụ như yêu cầu kê đơn thuốc, chẩn đoán bệnh...), hãy từ chối một cách lịch sự, thân thiện và khuyên người dùng nên tham khảo ý kiến bác sĩ chuyên khoa.\n"
            "3) Không dùng kiến thức bên ngoài, không đoán, không bịa thông tin y tế.\n"
            "4) Trả lời hoàn toàn bằng tiếng Việt.\n"
            "5) Khi có trích dẫn thông tin, BẠN BẮT BUỘC PHẢI trích dẫn bằng cách copy nguyên xi đoạn 'Mã trích dẫn' được cung cấp kèm theo nội dung. Tuyệt đối không tự chế định dạng trích dẫn khác.\n\n"
            "Ngữ cảnh:\n{context}\n\n"
            "Câu hỏi: {question}"
        )
        
        self.prompt = ChatPromptTemplate.from_template(template)
        
        # Using a valid OpenAI model (gpt-4o-mini is optimal for cost/performance)
        # gpt-5-mini does not exist yet.
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0
        )
        
        self.rag_chain = (
            {
                "context": self.retriever | self.format_docs,
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def format_docs(self, docs):
        import urllib.parse
        import os
        formatted = []
        for doc in docs:
            source = doc.metadata.get("source", "Không rõ nguồn")
            page = doc.metadata.get("page", "Không rõ trang")
            content = doc.page_content
            filename = os.path.basename(source)
            url_filename = urllib.parse.quote(filename)
            url = f"http://localhost:8000/api/papers/{url_filename}#page={page}"
            citation_format = f"[{filename} (Trang {page})]({url})"
            formatted.append(f"Mã trích dẫn: {citation_format}\nNội dung: {content}")
        return "\n\n".join(formatted)

    def get_answer(self, question: str) -> str:
        return self.rag_chain.invoke(question)

chat_service = ChatService()
