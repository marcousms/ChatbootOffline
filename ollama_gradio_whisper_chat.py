#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ollama Chat – UI moderne + audio → transcription (local)     Gradio ≥4.44
"""

import datetime, requests, gradio as gr
from gradio.themes import Soft, utils
from faster_whisper import WhisperModel                     # ↖ 1
# ---------- Réglages --------------------------------------------------
OLLAMA_HOST = "http://localhost:11434"
PORT        = 7860
ASR_SIZE    = "base"      # tiny | base | small | medium | large
# ---------- Charger Whisper une seule fois ---------------------------
print("Loading faster-whisper…")
asr = WhisperModel(ASR_SIZE, device="cpu")                  # ↖ 2
# ---------- Thème & CSS ----------------------------------------------
THEME = Soft(primary_hue=utils.colors.indigo,
             secondary_hue=utils.colors.emerald,
             neutral_hue=utils.colors.gray)
CSS = """
#header { @apply bg-gradient-to-r from-indigo-500 via-indigo-400 to-emerald-400
                  text-white p-[10px]; }
.chatbot .message.user { background:rgba(99,102,241,.15); }
.chatbot .message.bot  { background:rgba(16,185,129,.15); }
#send-btn { min-width:42px; padding:0 10px }
"""
# ---------- Ollama helpers -------------------------------------------
def list_models():
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        r.raise_for_status()
        return sorted(m["name"] for m in r.json()["models"])
    except Exception as e:
        print("[models]", e)
        return []
def ollama_chat(model, history, user_msg):
    msgs = [m for u, a in history
               for m in ({"role":"user","content":u},
                         {"role":"assistant","content":a})]
    msgs.append({"role":"user","content":user_msg})
    try:
        r = requests.post(f"{OLLAMA_HOST}/api/chat",
                          json={"model":model,"messages":msgs,"stream":False},
                          timeout=300)
        r.raise_for_status()
        assistant = r.json()["message"]["content"]
    except Exception as e:
        assistant = f"❌ Erreur : {e}"
    history.append((user_msg, assistant))
    return history, history
def init_hist():
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return [[f"👋 Bienvenue ! (UI {ts})", ""]], []
# ---------- Transcription --------------------------------------------
def transcribe(file_path):
    if file_path is None: return ""
    segments, _ = asr.transcribe(file_path)
    return " ".join(s.text.strip() for s in segments)
# ---------- Interface -------------------------------------------------
with gr.Blocks(theme=THEME, css=CSS, title="Ollama Chat + Audio") as demo:
    with gr.Row(elem_id="header"):
        gr.Markdown("## 🦙 Local LLM Chat + 🎙 ASR")
        models = gr.Dropdown(choices=list_models(), label="Modèles", scale=1)
    chatbot = gr.Chatbot(height=420, elem_classes="chatbot",
                         type="tuples")                      # ↖ 3
    with gr.Row():
        mic   = gr.Audio(sources=["microphone"], type="filepath",  # ↖ 4
                         label="Enregistrez puis cliquez Transcrire")
        trans = gr.Button("🗣 Transcrire")
    with gr.Row(equal_height=True):
        txt  = gr.Textbox(lines=1, placeholder="Texte ou transcription…",
                          autofocus=True, container=False)
        send = gr.Button("✈", variant="primary", size="sm", elem_id="send-btn")
    state = gr.State([])
    # —— callbacks ——
    trans.click(transcribe, mic, txt)                        # audio → texte
    models.change(lambda *_: init_hist(), None, [chatbot, state])
    clear = lambda: ""
    send.click(ollama_chat, [models, state, txt], [chatbot, state])\
        .then(clear, None, txt)
    txt.submit(ollama_chat, [models, state, txt], [chatbot, state])\
        .then(clear, None, txt)
    chatbot.value, state.value = init_hist()
# ---------- Lancement -------------------------------------------------
if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=PORT, inbrowser=True)
