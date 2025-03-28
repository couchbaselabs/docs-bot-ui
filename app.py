import streamlit as st
import requests
import json
import uuid
import platform
from typing import List, Dict

# Configure the page
st.set_page_config(
    page_title="Docs ChatBot",
    page_icon="📚",
    layout="wide"
)

# Constants
API_BASE_URL = st.secrets.get("app", {}).get("api_base_url1", "http://localhost:8000")

def generate_user_id() -> str:
    """Generate a unique user ID based on machine information."""
    # Combine system info to create a unique identifier
    system_info = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
    # Create a UUID based on the system info
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, system_info))

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["app"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password only
    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = generate_user_id()
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "run_id" not in st.session_state:
        st.session_state.run_id = str(uuid.uuid4())

def send_message(message: str) -> Dict:
    """Send message to the API and get response."""
    try:
        # Generate a new run_id for each message
        current_run_id = str(uuid.uuid4())
        st.session_state.run_id = current_run_id
        
        payload = {
            "data": {
                "thread_id": st.session_state.thread_id,
                "user_id": st.session_state.user_id,
                "run_id": current_run_id,
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
    if not check_password():
        st.stop()  # Do not continue if check_password() returned False

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