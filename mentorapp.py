import streamlit as st
from supabase import create_client
from groq import Groq
from pypdf import PdfReader

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="MentorAI SaaS 🚀", layout="wide")
st.title("🚀 MentorAI")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =========================
# SESSION STATE
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# =========================
# AUTH (MAGIC LINK)
# =========================
def send_magic_link(email):
    return supabase.auth.sign_in_with_otp({
        "email": email
    })

# =========================
# PDF
# =========================
def read_pdf(file):
    reader = PdfReader(file)
    return "".join([p.extract_text() or "" for p in reader.pages])

# =========================
# AI
# =========================
def ask_ai(prompt):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are MentorAI 🚀"},
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content

# =========================
# SUPABASE SAVE
# =========================
def save_message(user_id, role, content):
    supabase.table("messages").insert({
        "user_id": user_id,
        "role": role,
        "content": content
    }).execute()

# =========================
# LOAD MESSAGES
# =========================
def load_messages(user_id):
    res = supabase.table("messages") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("id") \
        .execute()
    return res.data

# =========================
# AUTH PAGE
# =========================
if st.session_state.user is None:

    st.markdown("## 🔐 Login with Email (Magic Link)")

    email = st.text_input("Enter your email")

    if st.button("Send Login Link"):
        try:
            send_magic_link(email)
            st.success("📩 Magic link sent! Check your email.")
        except:
            st.error("Failed to send link")

    st.markdown("---")
    st.info("After clicking email link, refresh this page.")

    st.stop()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.success(f"User: {st.session_state.user[:8]}")

    if st.button("Logout"):
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()

    file = st.file_uploader("Upload PDF", type=["pdf"])
    if file:
        st.session_state.pdf_text = read_pdf(file)
        st.success("PDF Loaded ✔")

# =========================
# CHAT UI
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask MentorAI...")

# =========================
# PROCESS CHAT
# =========================
if user_input:

    user_id = st.session_state.user

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    save_message(user_id, "user", user_input)

    context = st.session_state.pdf_text

    reply = ask_ai(f"{context}\n\nUser: {user_input}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    save_message(user_id, "assistant", reply)

    st.rerun()