import streamlit as st
from model.agent import Agent

chat_types = ['Apollo','Athena','Ares','Aphrodite','Hades','Hermes','Poseidon','Zeus']

selected_chat_type = st.sidebar.radio("Select Greek God:", chat_types,on_change=st.session_state.clear)

# Custom CSS for the chat container
st.markdown("""
    <style>
    .chat-container {
        overflow-y: auto;
        max-height: 400px; /* Adjust the height as needed */
    }
    .wrapper {
        word-wrap: break-word;
        white-space: pre-line;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to format and display text in a scrollable container
def display_text(messages):
    chat_html = '<div class="chat-container">'
    for message in messages:
        formatted_text = f"<b>{selected_chat_type if message['entity']=='ai' else 'user'}:</b> {message['message']}<br>"
        chat_html += f'<div class="wrapper">{formatted_text}</div><hr>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)
    
    

# Function to initialize the AI bot
def init_ai_bot():
    api_key=st.secrets["API_KEY"]
    api_org=st.secrets["API_ORG"]
    return Agent(api_key,api_org)  # Adjust as per your specific AI setup

# Streamlit app layout
st.title(selected_chat_type)


# Initialize AI bot once and store in session state
if 'ai_bot' not in st.session_state:
    st.session_state['ai_bot'] = init_ai_bot()
if 'count' not in st.session_state:
	st.session_state.count = 3

st.text(f"Time until portal closes:{st.session_state.count}")
# Function to get AI response
def get_ai_response(message):
    response = st.session_state['ai_bot'].get_response(message,st.session_state['history'][:-1],selected_chat_type,st.session_state.count)  # Adjust based on your AI's method
    st.session_state.count-=1
    return response



# Chat history display
if 'history' not in st.session_state:
    st.session_state['history'] = [{'entity':'ai','message':st.session_state['ai_bot'].get_intro(selected_chat_type)}]

def handle_input():
    if (st.session_state.count<=0):
        return
    user_input = st.session_state.user_input

    if user_input:
        st.session_state['history'].append({"entity": "user", "message": user_input})

        ai_response = get_ai_response(user_input)
        st.session_state['history'].append({"entity": "ai", "message": ai_response})
        if st.session_state.count<=0:
            st.session_state['history'].append({'entity':'ai','message':st.session_state['ai_bot'].get_evaluation(st.session_state['history'],selected_chat_type)})
        st.session_state.user_input = ""

display_text(st.session_state['history'])

user_input = st.text_input("Your message:", key="user_input", on_change=handle_input)
    