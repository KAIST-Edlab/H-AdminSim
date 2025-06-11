import requests
import streamlit as st
from sconf import Config
from streamlit_chat import message



# Initialize
config_path = 'config/llm_server.yaml'
config = Config(config_path)
API_URL = f'http://{config.host}:{config.port}/llm_response'
times = []


# Initialize session states
def initialize_session():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


# Reset session state
def reset_session():
    st.session_state.chat_history = []
    st.success('Session has been reset.')


# Send user prompt via FastAPI
def send_message_to_chatbot(api_request_data):
    try:
        response = requests.post(API_URL, json=api_request_data)
        response = response.json()
        return response
    
    except Exception as e:
        st.error(f'Error: {e}')
        return 'Error occurred while communicating with the server.'



# ------------------- Page design -------------------
st.set_page_config(layout='wide')  # 전체 화면 사용

# Session inicialization
initialize_session()

# Divide the page into two columns
col1, col2 = st.columns([1, 2])

# TODO: Patient conditions
with col1:
    st.header('TODO: Patient Conditions')


# Chat interface
with col2:
    st.header('💬 Reservation Agent')
    
    # Init necessaries
    chat_history_expander = st.expander('Chat History', expanded=True)

    # Chat input and button
    with st.form('form', clear_on_submit=True):
        user_input = st.text_input('Chatbot: ', '', key='input')
        submit_button = st.form_submit_button('Send')

        with chat_history_expander:
            # User input
            if submit_button and user_input.strip() != '':
                st.session_state.chat_history.append({'content': user_input, 'type': 'user'})
                response = send_message_to_chatbot({'user_prompt': user_input})
                response = response.get('response', "No response field in the server's reply.")
                st.session_state.chat_history.append({'content': response, 'type': 'bot'})

            # Logging all previous conversations
            for i, past_chat in enumerate(st.session_state.chat_history):
                if past_chat['type'] == 'bot':
                    message(past_chat['content'], key=f'bot_{i}')
                else:
                    message(past_chat['content'], is_user=True, key=f'user_{i}')
