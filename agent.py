import os
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter
from pathlib import Path

class RealEstateAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4-0125-preview",
            temperature=0.7
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings()
        
        # Load and process knowledge base
        texts_dir = os.path.join(os.path.dirname(__file__), "texts")
        if os.path.exists(texts_dir):
            # Get all text files
            text_files = []
            for file in os.listdir(texts_dir):
                if file.endswith('.txt'):
                    text_files.append(os.path.join(texts_dir, file))
            
            if not text_files:
                print("Warning: No text files found in texts directory")
                documents = []
            else:
                # Load all documents
                documents = []
                for file_path in text_files:
                    try:
                        loader = TextLoader(file_path, encoding='utf-8')
                        documents.extend(loader.load())
                    except Exception as e:
                        print(f"Error loading {file_path}: {e}")
            
            # Split text into chunks
            text_splitter = CharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separator="\n"
            )
            texts = text_splitter.split_documents(documents)
            
            if texts:
                # Create vector store
                self.vectorstore = FAISS.from_documents(texts, self.embeddings)
            else:
                print("Warning: No text content to process")
                # Create an empty vector store
                self.vectorstore = FAISS.from_texts(["No knowledge base available."], self.embeddings)
        else:
            print(f"Warning: texts directory not found at {texts_dir}")
            # Create an empty vector store
            self.vectorstore = FAISS.from_texts(["No knowledge base available."], self.embeddings)
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize retrieval chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 3}  # 상위 3개의 관련 문서 검색
            ),
            memory=self.memory,
            verbose=True
        )

    def _create_prompt(self, query: str) -> str:
        """Create a prompt for the chat model"""
        return f"""당신은 부동산 전문 AI 상담사입니다. 
주어진 문서들을 기반으로 사용자의 질문에 친절하고 상세하게 답변해주세요.

답변 시 다음 사항을 지켜주세요:
1. 전문적이고 정확한 정보를 제공하되, 이해하기 쉽게 설명해주세요.
2. 가능한 한 구체적인 예시나 수치를 포함해서 설명해주세요.
3. 필요한 경우 장단점이나 여러 관점을 함께 설명해주세요.
4. 법적/제도적 내용이 포함된 경우 관련 근거를 언급해주세요.
5. 답변을 적절한 문단으로 구분하여 가독성 있게 작성해주세요.

사용자 질문: {query}

관련 문서 내용:
{self._get_relevant_context(query)}

위 내용을 바탕으로 답변해주세요."""

    def _get_relevant_context(self, query: str) -> str:
        """Get relevant context from the knowledge base"""
        docs = self.chain.retriever.get_relevant_documents(query)
        return "\n\n".join([doc.page_content for doc in docs])

    def get_response(self, question: str) -> str:
        """
        사용자의 질문에 대한 답변을 생성합니다.
        """
        try:
            prompt = self._create_prompt(question)
            response = self.chain({"question": prompt})
            
            if not response or 'answer' not in response:
                return "죄송합니다. 답변을 생성하는 데 실패했습니다."
                
            return response['answer'].strip()
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'rate limit' in error_msg:
                return "죄송합니다. 현재 API 사용량이 한도에 도달했습니다. 잠시 후 다시 시도해주세요. (약 1시간 후)"
            else:
                return f"죄송합니다. 답변 생성 중 오류가 발생했습니다: {str(e)}"
