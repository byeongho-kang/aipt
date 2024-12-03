import streamlit as st
import os
import sys
from dotenv import load_dotenv
from agent import RealEstateAgent
import logging

# Disable all logging
logging.getLogger().setLevel(logging.ERROR)

# Redirect stderr to devnull
stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="BJSG AI Agient",
    page_icon="🏠",
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Load and apply custom CSS
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path, 'r', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def main():
    st.title("BJSG AI Agient")
    initialize_session_state()

    # Initialize agent
    agent = RealEstateAgent()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("무엇이든 물어보세요!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = agent.get_response(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
