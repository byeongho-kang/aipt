import os
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from typing import List
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

    def get_response(self, question: str) -> str:
        """
        사용자의 질문에 대한 답변을 생성합니다.
        """
        try:
            response = self.chain({"question": question})
            return response['answer']
        except Exception as e:
            print(f"Error generating response: {e}")
            return "죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다. 다시 질문해 주시겠습니까?"
