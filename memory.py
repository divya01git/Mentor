import streamlit as st

def init():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def add(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def get():
    return st.session_state.messages