# Nova AI Chat — LLM API Application

Nova AI Chat is a conversational AI web application built with Python, Streamlit, and the OpenAI API. It demonstrates API authentication, conversation history, system instructions, model settings, error handling, and token usage monitoring.

## Features

- Interactive AI chat interface
- Conversation history during the active Streamlit session
- Custom system instructions
- Selectable model, creativity, and response token limit
- API key loaded from environment variables or Streamlit secrets
- Handling for authentication errors, API errors, and quota/rate limits
- Latest response token usage
- Starter prompts and new-conversation control
- Responsive Streamlit layout

## Project structure

```text
llm-ai-chat-app/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create a virtual environment (recommended):

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **Windows Command Prompt**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and add your API key:

   ```env
   OPENAI_API_KEY=your_actual_api_key_here
   ```

6. Start the app:

   ```bash
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

1. Upload the project files to a GitHub repository.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Create an app and choose your repository, branch (`main`), and main file (`app.py`).
4. In the app's settings, open **Secrets** and add:

   ```toml
   OPENAI_API_KEY = "your_actual_api_key_here"
   ```

5. Deploy and test the public URL.

The app reads the key from environment variables first and then from Streamlit secrets. Never put a real API key in source code, a README, screenshots, or GitHub commits.

## Notes

- API access and billing are separate from a ChatGPT subscription. API usage may incur charges.
- The model list in `app.py` contains example model names. Model access can vary by account; update the list if needed.
- Chat history is kept in Streamlit session state. It is not permanently stored in a database.
- Token usage shown is for the latest successful response and is not a complete cost report.
- The application does not automatically retry failed API requests.

## Future improvements

- Save chat history in a database
- Export conversations
- Stream responses as they are generated
- Add user authentication
- Add a more detailed cost estimator
- Add support for other LLM providers

## Learning outcomes

This project demonstrates Python application development, LLM API integration, secure configuration, conversation management, error handling, and basic API usage monitoring.
