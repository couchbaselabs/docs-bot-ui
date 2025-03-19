import streamlit as st
import requests
import json
from typing import List, Dict

# Configure the page
st.set_page_config(
    page_title="Docs ChatBot",
    page_icon="📚",
    layout="wide"
)

# Constants
API_BASE_URL = "http://localhost:8000"

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = "id2"  # Default thread ID
    if "user_id" not in st.session_state:
        st.session_state.user_id = "userId1"  # Default user ID
    if "run_id" not in st.session_state:
        st.session_state.run_id = "runId1"  # Default run ID

def send_message(message: str) -> Dict:
    """Send message to the API and get response."""
    try:
        payload = {
            "data": {
                "thread_id": st.session_state.thread_id,
                "user_id": st.session_state.user_id,
                "run_id": st.session_state.run_id,
                "messages": message
            }
        }
        response = requests.post(
            f"{API_BASE_URL}/docs/rag_chat",
            json=payload
        )
        print(response.json())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the API: {str(e)}")
        return None

def main():
    st.title("📚 Docs ChatBot")
    st.markdown("""
    Welcome to the Docs ChatBot! Ask me anything about the documentation.
    I'll help you find the information you need.
    """)

    # Initialize session state
    initialize_session_state()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(prompt)
                if response:
                    response_text = response.get("content", "I apologize, but I couldn't process your request.")
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

    # Sidebar with information
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This is a ChatBot interface for the documentation system.
        It helps you find relevant information from the documentation.
        """)

if __name__ == "__main__":
    main() 