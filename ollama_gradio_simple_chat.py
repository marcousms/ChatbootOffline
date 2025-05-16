#!/usr/bin/env python
# coding: utf-8
"""
Ollama Chat – Modern UI sans bouton Refresh (Gradio ≥ 4.26)
"""

import datetime
import requests
import gradio as gr
from gradio.themes import Soft, utils

# ───── CONFIG
OLLAMA_HOST = "http://localhost:11434"
GRADIO_PORT = 7860

# ───── THEME & CSS
THEME = Soft(
    primary_hue   = utils.colors.indigo,
    secondary_hue = utils.colors.emerald,
    neutral_hue   = utils.colors.gray,
    radius_size   = utils.sizes.radius_md,
    spacing_size  = utils.sizes.spacing_md,
    text_size     = utils.sizes.text_md,
)
EXTRA_CSS = """
#header { @apply bg-gradient-to-r from-indigo-500 via-indigo-400 to-emerald-400
                  text-white p-[10px]; }
.chatbot .message.user { background:rgba(99,102,241,.15); }
.chatbot .message.bot  { background:rgba(16,185,129,.15); }
#send-btn { min-width:42px; padding:0 10px; }
"""

# ───── UTILITAIRES
def fetch_models():
    """Liste triée des modèles locaux Ollama (ou liste vide)."""
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        r.raise_for_status()
        return sorted(m["name"] for m in r.json().get("models", []))
    except Exception as exc:
        print("[fetch_models]", exc)
        return []

def ollama_chat(model, history, user_msg):
    """Appelle /api/chat et renvoie l’historique mis à jour."""
    msgs = [
        m  # flatten
        for u, a in history
        for m in ({"role": "user", "content": u},
                  {"role": "assistant", "content": a})
    ] + [{"role": "user", "content": user_msg}]

    try:
        r = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={"model": model, "messages": msgs, "stream": False},
            timeout=300,
        )
        r.raise_for_status()
        assistant = r.json()["message"]["content"]
    except Exception as exc:
        assistant = f"❌ Erreur : {exc}"

    history.append((user_msg, assistant))
    return history, history  # (chatbot, state)

def init_history():
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return [[f"👋 Bienvenue ! (UI lancée {ts})", ""]], []

# ───── INTERFACE
with gr.Blocks(theme=THEME, css=EXTRA_CSS, title="Ollama Chat") as demo:
    # Header (plus de bouton Refresh)
    with gr.Row(elem_id="header"):
        gr.Markdown("## 🦙 Local LLM Chat")
        models = gr.Dropdown(
            choices=fetch_models(),
            label="Modèles",
            scale=1
        )

    # Chat zone
    chatbot = gr.Chatbot(height=440, elem_classes="chatbot")

    # Input zone
    with gr.Row(equal_height=True):
        txt = gr.Textbox(
            lines=1,
            placeholder="Écris ici…  (Enter : envoyer, Shift+Enter : retour)",
            autofocus=True,
            container=False,
        )
        send = gr.Button("✈", variant="primary", size="sm", elem_id="send-btn")

    # Historique caché
    state = gr.State([])

    # Callbacks
    models.change(lambda *_: init_history(), None, [chatbot, state])

    clear = lambda: ""
    send.click(ollama_chat, [models, state, txt], [chatbot, state]).then(clear, None, txt)
    txt.submit(ollama_chat, [models, state, txt], [chatbot, state]).then(clear, None, txt)

    # Initialisation
    chatbot.value, state.value = init_history()

# ───── LANCEMENT
if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=GRADIO_PORT,
        inbrowser=True,
    )
