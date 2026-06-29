import streamlit as st
from groq import Groq
from pypdf import PdfReader

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="MentorAI 🚀", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# =========================
# PDF LOADER
# =========================
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# =========================
# AI FUNCTION
# =========================
def ask_ai(prompt):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are MentorAI, a helpful AI learning assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content

# =========================
# HEADER
# =========================
st.markdown("""
# 🚀 MentorAI
### AI Learning Assistant for Students & Creators
""")

st.divider()

# =========================
# SIDEBAR (CLEAN - NO CONFUSION)
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Controls")

    mode = st.radio("Choose Mode", [
        "💬 Chat Mode",
        "📚 Study Mode",
        "📄 PDF Assistant"
    ])

    file = st.file_uploader("Upload PDF", type=["pdf"])
    if file:
        st.session_state.pdf_text = read_pdf(file)
        st.success("PDF Loaded ✔")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# =========================
# CHAT UI (SAFE RENDER - NO CUT TEXT)
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# INPUT
# =========================
user_input = st.chat_input("Ask MentorAI anything...")

# =========================
# RESPONSE LOGIC
# =========================
if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    context = st.session_state.pdf_text

    if mode == "📄 PDF Assistant":
        prompt = f"Answer ONLY from this PDF:\n\n{context}\n\nQuestion: {user_input}"
    else:
        prompt = user_input

    reply = ask_ai(prompt)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    st.rerun()

# =========================
# MODE INFO (CLEAN UX ONLY)
# =========================
st.sidebar.markdown("---")
st.sidebar.caption("MentorAI runs in demo mode • No login required for now")