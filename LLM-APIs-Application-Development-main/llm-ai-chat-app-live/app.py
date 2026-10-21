import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError

# Load local .env when running on your computer.
load_dotenv()

st.set_page_config(
    page_title="Nova AI Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
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

# ---------- Secrets / API client ----------
def get_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("OPENAI_API_KEY")
    except Exception:
        return None


api_key = get_api_key()

# ---------- Session state ----------
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

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ⚙️ Chat settings")
    model = st.selectbox(
        "AI model",
        options=["gpt-4.1-mini", "gpt-4.1"],
        index=0,
        help="The selected model must be available to your API account.",
    )
    temperature = st.slider(
        "Creativity", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
        help="Higher values generally produce more varied answers.",
    )
    max_tokens = st.slider(
        "Maximum response tokens", min_value=100, max_value=2000,
        value=800, step=100,
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
        "Your API key is never displayed in the app. Do not place secrets in "
        "source code or upload a .env file to GitHub."
    )
    st.markdown("### 🧰 Built with")
    st.caption("Python · Streamlit · OpenAI API")

# ---------- Main UI ----------
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
        "The API key is not configured yet. Add OPENAI_API_KEY to your local "
        ".env file or to your Streamlit deployment secrets, then restart/redeploy."
    )
    st.stop()

client = OpenAI(api_key=api_key)

# Show previous conversation.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Suggested starter prompts.
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
            if st.button(prompt, use_container_width=True, key=f"starter_{idx}"):
                st.session_state.pending_prompt = prompt
                st.rerun()

pending_prompt = st.session_state.pop("pending_prompt", None)
user_input = st.chat_input("Message Nova AI...")
if pending_prompt:
    user_input = pending_prompt

if user_input:
    st.session_state.last_error = None
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    api_messages = [
        {"role": "system", "content": st.session_state.custom_instructions},
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
                    "Authentication failed. Check that your API key is correct "
                    "and active."
                )
                st.error(st.session_state.last_error)
            except RateLimitError:
                st.session_state.last_error = (
                    "The API rate limit or quota was reached. Check API usage, "
                    "billing, and limits in your API account."
                )
                st.error(st.session_state.last_error)
            except APIError as exc:
                st.session_state.last_error = (
                    f"The AI service returned an API error ({type(exc).__name__}). "
                    "Try again later or check the selected model."
                )
                st.error(st.session_state.last_error)
            except Exception as exc:
                # Avoid displaying secrets or raw request details to users.
                st.session_state.last_error = (
                    f"Could not complete the request ({type(exc).__name__}). "
                    "Check your connection and app configuration."
                )
                st.error(st.session_state.last_error)

# Token details for the latest successful API response.
if st.session_state.last_usage:
    with st.expander("📊 Latest API token usage"):
        usage = st.session_state.last_usage
        u1, u2, u3 = st.columns(3)
        u1.metric("Input tokens", usage["input_tokens"])
        u2.metric("Output tokens", usage["output_tokens"])
        u3.metric("Total tokens", usage["total_tokens"])
        st.caption(
            "This displays token usage for the latest successful response, not "
            "a full bill. Actual API costs depend on model pricing."
        )

st.divider()
st.markdown(
    '<p class="small-note">Nova AI Chat · Built as an LLM API learning project. '
    'AI responses may be incorrect; verify important information.</p>',
    unsafe_allow_html=True,
)
