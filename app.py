import streamlit as st
import os
from dotenv import load_dotenv
from agent import RealEstateAgent
from typing import List, Dict

# Load environment variables
load_dotenv()

# Constants
APP_TITLE = "BJSG AI Agent"
APP_ICON = "🏠"
INPUT_PLACEHOLDER = "무엇이든 물어보세요!"

class ChatInterface:
    def __init__(self):
        self._configure_page()
        self._load_css()
        self._initialize_session_state()
        self.agent = RealEstateAgent()

    def _configure_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=APP_TITLE,
            page_icon=APP_ICON,
            layout="wide",
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': None
            }
        )

    def _load_css(self):
        """Load and apply custom CSS"""
        css_path = os.path.join(os.path.dirname(__file__), "style.css")
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    def _initialize_session_state(self):
        """Initialize session state for chat messages"""
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def _add_message(self, role: str, content: str):
        """Add a message to the chat history"""
        st.session_state.messages.append({"role": role, "content": content})

    def _display_message(self, message: Dict[str, str]):
        """Display a single chat message"""
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    def _display_chat_history(self):
        """Display all messages in the chat history"""
        for message in st.session_state.messages:
            self._display_message(message)

    def _handle_user_input(self, prompt: str):
        """Process user input and generate response"""
        try:
            # Add user message
            self._add_message("user", prompt)
            
            # Show spinner while generating response
            with st.spinner('답변을 생성하고 있습니다...'):
                response = self.agent.get_response(prompt)
                
                if response:
                    self._add_message("assistant", response)
                else:
                    self._add_message("assistant", "죄송합니다. 답변을 생성하는 데 문제가 발생했습니다.")
            
            # Display updated chat history
            st.rerun()
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")

    def run(self):
        """Run the chat interface"""
        st.title(APP_TITLE)
        
        # Display chat history
        self._display_chat_history()
        
        # Chat input at the bottom
        if prompt := st.chat_input(INPUT_PLACEHOLDER):
            self._handle_user_input(prompt)

def main():
    chat_interface = ChatInterface()
    chat_interface.run()

if __name__ == "__main__":
    main()
