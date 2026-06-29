from groq import Groq
import streamlit as st

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ask_ai(messages):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return res.choices[0].message.content