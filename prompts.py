def build_prompt(context, user_input):
    return f"""
You are MentorAI, a smart AI mentor.

Context:
{context}

User:
{user_input}

Answer clearly and step-by-step.
"""