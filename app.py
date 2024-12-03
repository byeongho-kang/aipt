import os
import streamlit as st
from dotenv import load_dotenv
from agent import RealEstateAgent
import openai
from pydub import AudioSegment
import tempfile

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set page config
st.set_page_config(
    page_title="부동산 투자 AI 상담",
    page_icon="🏠",
    layout="wide"
)

# Load and apply custom CSS
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path, 'r', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = RealEstateAgent()
if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title("부동산 투자 AI 상담")

# Sidebar for menu selection
menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["AI 상담사", "음성 파일 변환"]
)

if menu == "AI 상담사":
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Text input for chat
    if prompt := st.chat_input("질문을 입력하세요"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner('AI가 답변을 생성하고 있습니다...'):
            response = st.session_state.agent.get_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})

elif menu == "음성 파일 변환":
    st.header("음성 파일을 텍스트로 변환")
    
    # Audio file uploader
    audio_file = st.file_uploader("음성 파일을 업로드하세요 (WAV 또는 MP3)", type=['wav', 'mp3'])

    if audio_file is not None:
        if st.button("변환 시작"):
            # Create a temporary file to save the uploaded audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
                tmp_file.write(audio_file.getvalue())
                tmp_path = tmp_file.name

            try:
                # Convert MP3 to WAV if necessary
                if audio_file.type == 'audio/mp3':
                    audio = AudioSegment.from_mp3(tmp_path)
                    wav_path = tmp_path.rsplit('.', 1)[0] + '.wav'
                    audio.export(wav_path, format='wav')
                    tmp_path = wav_path

                # Transcribe audio file
                with st.spinner("음성을 텍스트로 변환 중..."):
                    with open(tmp_path, 'rb') as audio_file:
                        transcript = openai.Audio.transcribe("whisper-1", audio_file)
                        
                    if transcript and transcript.text:
                        # Show the transcribed text
                        st.subheader("변환된 텍스트:")
                        st.text_area("", transcript.text, height=200)
                        
                        # Option to send to AI agent
                        if st.button("AI 상담사에게 질문하기"):
                            st.session_state.messages.append({"role": "user", "content": transcript.text})
                            
                            with st.spinner('AI가 답변을 생성하고 있습니다...'):
                                response = st.session_state.agent.get_response(transcript.text)
                                st.session_state.messages.append({"role": "assistant", "content": response})
                            
                            # Switch to AI consultant menu
                            st.experimental_set_query_params(menu="AI 상담사")
                            st.experimental_rerun()
            
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
            
            finally:
                # Clean up temporary files
                try:
                    os.unlink(tmp_path)
                    if 'wav_path' in locals():
                        os.unlink(wav_path)
                except:
                    pass
