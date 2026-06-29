import streamlit as st
from groq import Groq
from pypdf import PdfReader
import speech_recognition as sr
from supabase import create_client

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="MentorAI", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

st.success("✅ Supabase Connected")

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# =========================
# PDF READER
# =========================
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# =========================
# VOICE INPUT
# =========================
def voice_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except:
        return "Sorry, could not understand audio"

# =========================
# AI FUNCTION
# =========================
def ask_ai(prompt):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are MentorAI, a smart AI mentor."},
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content

# =========================
# UI HEADER
# =========================
st.title("🚀 MentorAI")
st.write("Supabase URL found:", "SUPABASE_URL" in st.secrets)
st.write("Supabase Key found:", "SUPABASE_KEY" in st.secrets)
st.write("Groq Key found:", "GROQ_API_KEY" in st.secrets)

# =========================
# SIDEBAR CONTROLS
# =========================
with st.sidebar:
    st.header("⚙️ Controls")

    mode = st.selectbox(
        "Choose Mode",
        ["💬 Chat", "📚 Study Plan", "📄 PDF Assistant"]
    )

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        st.session_state.pdf_text = read_pdf(uploaded_file)
        st.success("PDF Loaded ✔")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# =========================
# CHAT MODE
# =========================
if mode == "💬 Chat":

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    col1, col2 = st.columns([4, 1])

    with col1:
        user_input = st.chat_input("Ask anything...")

    with col2:
        mic = st.button("🎤 Mic")

    if mic:
        user_input = voice_to_text()
        st.write("🗣️ You said:", user_input)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        context = st.session_state.pdf_text

        prompt = f"""
Use the context if available:

{context}

User question:
{user_input}
"""

        reply = ask_ai(prompt)

        st.session_state.messages.append({"role": "assistant", "content": reply})

        st.rerun()

# =========================
# STUDY PLAN MODE
# =========================
elif mode == "📚 Study Plan":

    topic = st.text_input("Enter topic")

    if st.button("Generate Study Plan") and topic:

        prompt = f"""
Create a detailed structured study plan for: {topic}

Include:
- Beginner to advanced roadmap
- Daily/weekly structure
- Practice suggestions
"""

        result = ask_ai(prompt)

        st.write(result)

# =========================
# PDF ASSISTANT
# =========================
elif mode == "📄 PDF Assistant":

    question = st.chat_input("Ask from PDF")

    if question:

        context = st.session_state.pdf_text

        prompt = f"""
Answer only using this PDF context:

{context}

Question: {question}
"""

        answer = ask_ai(prompt)

        st.write(answer)