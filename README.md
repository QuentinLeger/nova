# Nova — Personal AI Assistant

> Voice-controlled AI assistant running across multiple devices, powered by LLaMA 3.3 via Groq.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Groq](https://img.shields.io/badge/LLM-Groq%20%2F%20LLaMA%203.3-orange?style=flat-square)
![Notion](https://img.shields.io/badge/Notion-API-black?style=flat-square&logo=notion)
![Flask](https://img.shields.io/badge/Flask-REST-green?style=flat-square&logo=flask)
![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)

---

## What is Nova ?

Nova is a personal AI assistant I built from scratch during my BUT studies.  
It listens to voice commands, understands natural language via a LLaMA 3.3 model (Groq API), and executes actions across multiple machines on my local network.

**Say "Nova, analyse ma dernière séance"** → Nova fetches your workout CSV, calls the LLM for coaching analysis, generates a next-session program, and reads a summary out loud.

**Say "Nova, ajoute une tâche demain"** → Nova adds it directly to your Notion database.

**Say "Nova, lance Steam sur le PC fixe"** →  Nova sends the command to the right machine over HTTP.

---

## Features

- 🎙️ **Voice recognition** — listens for wake word "Nova", transcribes with Google Speech API
- 🧠 **LLM routing** — every command is parsed by LLaMA 3.3 (Groq) into structured JSON actions
- 🖥️ **Multi-device control** — routes actions to pc_fixe or pc_portable via local Flask servers
- 📋 **Notion integration** — add, list, and delete tasks directly from voice
- 🏋️ **Workout analysis** — analyses training sessions from CSV, gives progression feedback and generates next session
- 🔊 **Edge TTS** — natural French voice synthesis (Microsoft Vivienne Neural)
- 🌐 **Web actions** — open sites, search YouTube/Google, launch apps, run macros

---

## Architecture

```
Nova/
├── backend/
│   ├── agents/
│   │   ├── mainNova.py      # Entry point — mode selection & action router
│   │   ├── audio.py         # parler() + ecouter() — voice I/O
│   │   ├── sport.py         # Workout analysis & next session generation
│   │   ├── notionTasks.py   # Notion API — tasks CRUD + gerer_taches()
│   │   └── server.py        # Flask server — /speak /execute /save_file
│   └── config/
│       └── portable.json    # Per-device app paths & macros
└── workouts.csv             # Hevy export — workout history
```

**Request lifecycle :**
```
Voice / Text input
      ↓
ask_nova()  →  Groq API (LLaMA 3.3)  →  JSON action
      ↓
executer()  →  routes to the right module
      ↓
audio / sport / notionTasks / send_to_device
```

---

## Tech Stack

| Layer | Tech |
|---|---|
| LLM | LLaMA 3.3 70B via Groq API |
| Voice in | SpeechRecognition + Google |
| Voice out | Edge TTS (Microsoft Neural) |
| Task management | Notion API |
| Device communication | Flask + HTTP |
| Workout data | Pandas + CSV (Hevy export) |
| Config | dotenv |

---

## Getting Started

```bash
git clone https://github.com/yourname/nova
cd nova
pip install -r requirements.txt
cp .env.example .env  # fill in your API keys
```

**.env required keys :**
```
GROQ_API_KEY=...
NOTION_API_KEY=...
NOTION_DATABASE_ID=...
```

**Run the device server** (on each machine you want to control) :
```bash
python backend/agents/server.py
```

**Run Nova :**
```bash
python backend/agents/mainNova.py
# → Mode (ecrit/oral) :
```

---

## Roadmap

- [ ] Frontend dashboard (workout graphs, task board)
- [ ] Auto-sync workouts via Hevy webhook
- [ ] Spotify / media control
- [ ] Memory across sessions (conversation history)
- [ ] Wake word detection without "nova" keyword

---

## About

Built by **Quentin** — BUT Informatique student.  
This project started as a personal automation tool and grew into a full multi-device AI assistant.  
All modules are loosely coupled — easy to extend with new skills.

---

*Nova is not affiliated with Groq, Notion, or Hevy.*
