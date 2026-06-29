import streamlit as st

class Config:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    MODEL = "llama-3.3-70b-versatile"