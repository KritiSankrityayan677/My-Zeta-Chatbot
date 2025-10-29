# app.py
import streamlit as st
from dotenv import load_dotenv
from utils import chat_with_zeta, recall_memory

load_dotenv()

st.set_page_config(page_title="Zeta — Your Context-Aware Chatbot", layout="wide")

# ------------------------------
# Initialize session state
# ------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {"bot_name": "Zeta", "user_id": "local_user", "name": None}

# ------------------------------
# UI
# ------------------------------
st.title("💫 Zeta — Your Context-Aware & Memory-Enabled Chatbot")
st.caption("Built with Gemini 2.0 Flash + LangChain + ChromaDB")

user_input = st.chat_input("Type something...")

if user_input:
    st.session_state.chat_history.append(("You", user_input))

    with st.spinner("Zeta is thinking..."):
        response = chat_with_zeta(user_input, st.session_state.user_profile)

    st.session_state.chat_history.append(("Zeta", response))

# ------------------------------
# Display chat
# ------------------------------
for role, msg in st.session_state.chat_history:
    if role == "You":
        with st.chat_message("user"):
            st.write(msg)
    else:
        with st.chat_message("assistant"):
            st.write(msg)

# ------------------------------
# Debug: View Memory
# ------------------------------
with st.expander("🧠 Recalled Memory (Debug)"):
    query = st.text_input("Query memory (debug):")
    if query:
        user_name = st.session_state.user_profile.get("name")
        mem = recall_memory(user_name, query) if user_name else recall_memory(query)
        if mem:
            st.markdown(mem)
        else:
            st.info("No relevant memory found.")

# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:
    st.header("⚙️ Options")
    if st.button("🔄 Reset Chat"):
        st.session_state.clear()
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("""
    **💡 About Zeta:**
    - 🧠 Remembers explicit facts you share  
    - 🔒 Refuses impossible/observational questions  
    - ❤️ Adapts tone & empathy  
    - 🌈 Keeps consistent, human-like personality  
    """)

