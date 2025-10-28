# app.py
import streamlit as st
from utils import chat_with_zeta, recall_memory
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Zeta", layout="wide")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {"bot_name": "Zeta", "user_id": "local_user"}

st.title("Zeta — Your Memory Chatbot")

# ask name once
if not st.session_state.user_profile.get("name"):
    name = st.text_input("What's your name?")
    if name:
        st.session_state.user_profile["name"] = name.strip()
        st.success(f"Nice to meet you, {name}!")

# chat input area
st.markdown("### Chat")
user_input = st.chat_input("Type something...")
if user_input:
    st.session_state.chat_history.append(("You", user_input))
    with st.spinner("Zeta is thinking..."):
        resp = chat_with_zeta(user_input, st.session_state.user_profile)
    st.session_state.chat_history.append(("Zeta", resp))

# display chat history (Streamlit chat messages)
for role, txt in st.session_state.chat_history:
    if role == "You":
        with st.chat_message("user"):
            st.write(txt)
    else:
        with st.chat_message("assistant"):
            st.write(txt)

# debug view
with st.expander("Recalled memory (debug)"):
    q = st.text_input("Query memory (debug):")
    if q:
        st.write(recall_memory(q))