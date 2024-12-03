import os
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class RealEstateAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4-1106-preview",
            temperature=0.7
        )
        
        # Load knowledge base
        knowledge_path = os.path.join(os.path.dirname(__file__), "texts", "real_estate_knowledge.txt")
        if os.path.exists(knowledge_path):
            with open(knowledge_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = f.read()
        else:
            self.knowledge_base = ""
        
        # Create prompt template
        template = """당신은 부동산 투자 전문가입니다. 

다음 지식을 기반으로 답변해주세요:
{knowledge_base}

{chat_history}
질문: {question}
답변: """

        # Initialize conversation memory and chain
        self.memory = ConversationBufferMemory(memory_key="chat_history", input_key="question")
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["chat_history", "question", "knowledge_base"],
                template=template
            ),
            memory=self.memory,
            verbose=True
        )

    def get_response(self, question: str) -> str:
        """
        사용자의 질문에 대한 답변을 생성합니다.
        """
        return self.chain.predict(
            question=question,
            knowledge_base=self.knowledge_base
        )

    def add_knowledge(self, text: str):
        """
        새로운 지식을 에이전트에 추가합니다.
        """
        self.knowledge_base += "\n" + text
