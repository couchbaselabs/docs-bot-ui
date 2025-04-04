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
API_BASE_URL = st.secrets.get("app", {}).get("api_base_url", "http://localhost:8000")

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
        if st.session_state["password"] == st.secrets["app"]["password"] and st.session_state.get("terms_accepted", False):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False
            if not st.session_state.get("terms_accepted", False):
                st.error("Please accept the Terms & Conditions")

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password and T&C checkbox
    st.text_input("Password", type="password", key="password")
    st.checkbox("I accept the [Privacy Policy](https://www.couchbase.com/privacy-policy/) and [Terms of Use](https://www.couchbase.com/terms-of-use/)", key="terms_accepted")
    
    # Add sign in button
    if st.button("Sign In"):
        password_entered()
        
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        if st.session_state["password"] != st.secrets["app"]["password"]:
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
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the API: {str(e)}")
        return None

# Not used right now in the app
def send_feedback(is_upvote: bool, feedback_text: str) -> Dict:
    """Send feedback to the API."""
    try:
        payload = {
            "data": {
                "thread_id": st.session_state.thread_id,
                "user_id": st.session_state.user_id,
                "run_id": st.session_state.run_id,
                "is_upvote": is_upvote,
                "feedback_text": feedback_text
            }
        }
        response = requests.post(
            f"{API_BASE_URL}/docs/feedback",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error sending feedback: {str(e)}")
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
            st.markdown(message["content"], unsafe_allow_html=True)

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
                    doc_source_urls = response.get("doc_source_urls", [])
                    doc_source_urls = set(doc_source_urls)
                    # Filter URLs to keep only the current version of the same document
                    filtered_urls = []
                    url_paths = {}
                    
                    for url in doc_source_urls:
                        # Extract the base path without version
                        parts = url.split('/')
                        
                        # Find the version part in the URL (like 'current', '7.1', '7.2', etc.)
                        product_idx = -1
                        version_idx = -1
                        
                        for i, part in enumerate(parts):
                            if part in ['server', 'sdk', 'couchbase-lite', 'sync-gateway', 'java-sdk', 'python-sdk', 'go-sdk', 'nodejs-sdk', 'dotnet-sdk', 'nodejs-sdk']:
                                product_idx = i
                                version_idx = i + 1
                                break
                        
                        if product_idx >= 0 and version_idx < len(parts):
                            # Get the document path without the version
                            version = parts[version_idx]
                            
                            # Create a key by replacing the version with a placeholder
                            parts_copy = parts.copy()
                            parts_copy[version_idx] = "VERSION"
                            doc_key = '/'.join(parts_copy)
                            
                            # Store the URL with its version
                            if doc_key not in url_paths or version == 'current' or (
                                url_paths[doc_key][1] != 'current' and version > url_paths[doc_key][1]
                            ):
                                url_paths[doc_key] = (url, version)
                        else:
                            # If we can't identify the version pattern, keep the URL as is
                            filtered_urls.append(url)
                    
                    # Add the filtered URLs (current version or latest version)
                    filtered_urls.extend([info[0] for info in url_paths.values()])
                    
                    # Use HTML <br> for line breaks within the same paragraph
                    source_link_string = "<br>".join(filtered_urls)
                    
                    # Combine all markdown content into a single string with HTML preserved
                    formatted_response = len(doc_source_urls) > 0 and f"{response_text}\n\n---\n\n**Sources:**\n\n{source_link_string}" or response_text
                    st.markdown(formatted_response, unsafe_allow_html=True)
                    
                    st.session_state.messages.append({"role": "assistant", "content": formatted_response})

    # Sidebar with information
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This is a ChatBot interface for the documentation system.
        It helps you find relevant information from the documentation.
        """)

if __name__ == "__main__":
    main() 