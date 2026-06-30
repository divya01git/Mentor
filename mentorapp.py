import streamlit as st
from groq import Groq
from pypdf import PdfReader
import speech_recognition as sr

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
            {"role": "system", "content": "You are MentorAI, a helpful AI mentor for students."},
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content
# =========================
# VOICE INPUT
# =========================
def voice_to_text():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening...")
            audio = r.listen(source, timeout=5)

        text = r.recognize_google(audio)
        return text

    except Exception:
        return None

# =========================
# HEADER (CLEAN BRAND STYLE)
# =========================
st.markdown("""
<div style="text-align:center; padding:10px;">
    <h1>🚀 MentorAI</h1>
    <p style="color:gray;">Your AI Learning & Study Companion</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# =========================
# SIDEBAR (MINIMAL CLEAN)
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Controls")

    mode = st.selectbox("Mode", [
        "💬 Chat",
        "📚 Study",
        "📄 PDF Assistant"
    ])

    file = st.file_uploader("Upload PDF", type=["pdf"])
    if file:
        st.session_state.pdf_text = read_pdf(file)
        st.success("PDF loaded ✔")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("MentorAI • Clean UI Demo")

# =========================
# =========================

# =========================
# CHAT DISPLAY (CHATGPT STYLE)
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
# INPUT BOX
# =========================
col1, col2 = st.columns([8, 1])

with col1:
    user_input = st.chat_input("Ask anything...")

with col2:
    mic = st.button("🎤")

    if mic:
        voice_text = voice_to_text()

        if voice_text:
            st.session_state.voice_text = voice_text

# =========================
# VOICE PREVIEW
# =========================
if "voice_text" in st.session_state:

    st.chat_message("user").markdown(
    f"🎤 {st.session_state.voice_text}"
)

    c1, c2 = st.columns(2)

    with c1:
        if st.button("✔ Send Voice"):
            user_input = st.session_state.voice_text
            del st.session_state.voice_text

    with c2:
        if st.button("❌ Cancel"):
            del st.session_state.voice_text

# =========================
# LOGIC
# =========================
if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    context = st.session_state.pdf_text

    if mode == "📄 PDF Assistant":
        prompt = f"""
Use only this PDF context:

{context}

Question: {user_input}
"""
    elif mode == "📚 Study":
        prompt = f"Create a structured explanation/study help for: {user_input}"
    else:
        prompt = user_input

    with st.chat_message("assistant"):

        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are MentorAI, a helpful AI mentor for students."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )

        response = st.write_stream(
            (chunk.choices[0].delta.content or "")
            for chunk in stream
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    st.rerun()