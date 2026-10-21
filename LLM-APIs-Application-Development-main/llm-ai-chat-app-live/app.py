
import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq, APIError, AuthenticationError, RateLimitError

load_dotenv()

st.set_page_config(
    page_title="Nova AI Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 1000px; padding-top: 2rem; padding-bottom: 3rem;}
      .hero {
        padding: 1.5rem 1.7rem; border-radius: 18px;
        background: linear-gradient(120deg, #eef5ff, #f3f0ff);
        border: 1px solid #dbe6f7; margin-bottom: 1.2rem;
      }
      .hero h1 {margin: 0; color: #152744; font-size: 2.2rem;}
      .hero p {margin: .5rem 0 0; color: #465875;}
      div[data-testid="stChatMessage"] {border-radius: 14px;}
      .small-note {color: #64748b; font-size: .88rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def get_api_key():
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("GROQ_API_KEY")
    except Exception:
        return None


api_key = get_api_key()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "custom_instructions" not in st.session_state:
    st.session_state.custom_instructions = (
        "You are a helpful AI assistant. Be accurate, clear, respectful, "
        "and beginner-friendly. If you are unsure, say so."
    )

if "last_usage" not in st.session_state:
    st.session_state.last_usage = None

if "last_error" not in st.session_state:
    st.session_state.last_error = None

with st.sidebar:
    st.markdown("## ⚙️ Chat settings")

    model = st.selectbox(
        "AI model",
        options=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ],
        index=0,
        help="The model must be available to your Groq account.",
    )

    temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
    )

    max_tokens = st.slider(
        "Maximum response tokens",
        min_value=100,
        max_value=2000,
        value=800,
        step=100,
    )

    st.session_state.custom_instructions = st.text_area(
        "Custom instructions",
        value=st.session_state.custom_instructions,
        height=140,
        help="These instructions guide the AI on future messages.",
    )

    if st.button("＋ New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_usage = None
        st.session_state.last_error = None
        st.rerun()

    st.divider()
    st.markdown("### 🔐 Privacy")
    st.caption(
        "Your API key is kept in app secrets. Never put it in source code "
        "or upload a .env file to GitHub."
    )
    st.markdown("### 🧰 Built with")
    st.caption("Python · Streamlit · Groq API")

st.markdown(
    """
    <div class="hero">
      <h1>🤖 Nova AI Chat</h1>
      <p>Your AI assistant for questions, learning, brainstorming, and everyday tasks.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Chat messages", len(st.session_state.messages))

with col2:
    st.metric("Selected model", model)

with col3:
    total = (
        st.session_state.last_usage["total_tokens"]
        if st.session_state.last_usage else 0
    )
    st.metric("Latest response tokens", total)

if not api_key:
    st.warning(
        "Groq API key not found. Add GROQ_API_KEY to your local .env "
        "file or Streamlit deployment secrets."
    )
    st.stop()

client = Groq(api_key=api_key)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.messages:
    st.markdown("#### Try asking")
    starter_cols = st.columns(3)

    starter_prompts = [
        "Explain Python in simple words",
        "Give me a beginner study plan for AI",
        "Help me prepare for a technical interview",
    ]

    for idx, prompt in enumerate(starter_prompts):
        with starter_cols[idx]:
            if st.button(
                prompt,
                use_container_width=True,
                key=f"starter_{idx}",
            ):
                st.session_state.pending_prompt = prompt
                st.rerun()

pending_prompt = st.session_state.pop("pending_prompt", None)
user_input = st.chat_input("Message Nova AI...")

if pending_prompt:
    user_input = pending_prompt

if user_input:
    st.session_state.last_error = None
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    api_messages = [
        {
            "role": "system",
            "content": st.session_state.custom_instructions,
        },
        *st.session_state.messages,
    ]

    with st.chat_message("assistant"):
        with st.spinner("Nova is thinking..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    temperature=temperature,
                    max_completion_tokens=max_tokens,
                )

                answer = response.choices[0].message.content or (
                    "The AI returned an empty response. Please try again."
                )

                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

                if response.usage:
                    st.session_state.last_usage = {
                        "input_tokens": response.usage.prompt_tokens,
                        "output_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }

            except AuthenticationError:
                st.session_state.last_error = (
                    "Groq authentication failed. Check GROQ_API_KEY "
                    "in Streamlit Secrets."
                )
                st.error(st.session_state.last_error)

            except RateLimitError:
                st.session_state.last_error = (
                    "Groq usage limit reached. Check your Groq Console "
                    "usage limits and model availability."
                )
                st.error(st.session_state.last_error)

            except APIError as exc:
                st.session_state.last_error = (
                    f"Groq API error ({type(exc).__name__}). "
                    "Check the selected model and try again."
                )
                st.error(st.session_state.last_error)

            except Exception as exc:
                st.session_state.last_error = (
                    f"Request failed ({type(exc).__name__}). "
                    "Check your app configuration."
                )
                st.error(st.session_state.last_error)

if st.session_state.last_usage:
    with st.expander("📊 Latest API token usage"):
        usage = st.session_state.last_usage
        u1, u2, u3 = st.columns(3)
        u1.metric("Input tokens", usage["input_tokens"])
        u2.metric("Output tokens", usage["output_tokens"])
        u3.metric("Total tokens", usage["total_tokens"])
        st.caption("Usage numbers are for the latest successful response.")

st.divider()
st.markdown(
    '<p class="small-note">Nova AI Chat · Built as an LLM API learning project. '
    'AI responses may be incorrect; verify important information.</p>',
    unsafe_allow_html=True,
)
