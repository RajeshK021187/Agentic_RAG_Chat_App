import streamlit as st
import requests

st.title("Local RAG Agentic Chat")

if "history" not in st.session_state:
    st.session_state.history = []

def ask_question():
    question = st.session_state.get("question", "").strip()
    if not question:
        st.warning("Please enter a question.")
        return

    try:
        response = requests.post(
            "http://localhost:8000/ask",
            json={"question": question}
        )
        response.raise_for_status()
        data = response.json()
        # Fix here: Use "answer" key to match FastAPI response
        answer = data.get("answer", "No answer received.")

        st.session_state.history.append(("You", question))
        st.session_state.history.append(("Agent", answer))
        st.session_state.question = ""

    except Exception as e:
        st.error(f"Error: {e}")

st.text_input("Ask anything about the database:", key="question", on_change=ask_question)

for speaker, text in st.session_state.history:
    if speaker == "You":
        st.markdown(f"**You:** {text}")
    else:
        st.markdown(f"**Agent:** {text}")
