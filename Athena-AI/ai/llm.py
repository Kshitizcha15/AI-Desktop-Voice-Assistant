import re
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3.5:9b"


def _clean_for_speech(text):
    """
    Strips common Markdown formatting the LLM might add,
    since TTS reads raw characters literally (e.g. saying "asterisk asterisk").
    """
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold** -> bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)        # *italic* -> italic
    text = re.sub(r'`(.*?)`', r'\1', text)          # `code` -> code
    text = re.sub(r'#{1,6}\s*', '', text)           # markdown headers
    return text.strip()


def ask_llm(user_text, history=None):
    """
    history: list of {"role": "user"/"assistant", "content": str}
    Returns the model's reply as a string, cleaned of Markdown for speech.
    """
    messages = (history or []) + [{"role": "user", "content": user_text}]

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": messages,
        "stream": False
    })
    response.raise_for_status()
    raw_reply = response.json()["message"]["content"]
    return _clean_for_speech(raw_reply)