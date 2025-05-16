# 🦙 Chatbot IA 100 % Local en 15 min

> Démonstration complète (installation ➜ API ➜ UI ➜ bonus vocal)  
> Public cible : curieux d’IA, devs, formateurs, mais aussi non-tech.

---

## 🌟 Pourquoi ce projet ?

| Problème                                                   | Solution apportée                         |
|------------------------------------------------------------|------------------------------------------|
| Faire tourner un LLM sans clé API ni cloud                 | **Ollama** sert les modèles localement   |
| Tester rapidement plusieurs modèles (Llama 3, Gemma…)      | Dropdown de sélection en un clic         |
| Partager une démo graphique sans se battre avec le front   | **Gradio** génère l’UI instantanément    |
| Ajouter la voix sans service externe                       | **Whisper** transcrit hors-ligne         |

---

## ✨ Fonctionnalités

- **Serveur Ollama** intégré : exécute et gère les modèles open-source.  
- **Chatbot Web** minimal (Gradio) : bulles, thème Soft, responsive.  
- **Sélecteur de modèles** : changez de LLM en temps réel, sans reload.  
- **Transcription vocale locale** (faster-whisper) : parlez, transcrivez, envoyez.  
- **100 % offline** : aucune donnée ne sort de la machine.  

---

## 📸 Capture d’écran

<p align="center">
 <img src="assets/screenshot_ui.png" width="600" alt="UI Gradio">
</p>

---

## 🚀 Installation rapide

```bash
# 1. Cloner
git clone https://github.com/<ton-user>/ollama-local-chat.git
cd ollama-local-chat

# 2. Installer dépendances Python
pip install -r requirements.txt   # gradio, requests, faster-whisper, ffmpeg-python

# 3. Installer Ollama et télécharger deux modèles
winget install Ollama             # ou brew / apt
ollama pull llama3
ollama pull gemma:7b

# 4. Lancer le serveur
ollama serve &                    # service HTTP sur :11434

# 5. Lancer l’interface
python ollama_chat_ui.py

# 6. Naviguer ➜ http://localhost:7860
