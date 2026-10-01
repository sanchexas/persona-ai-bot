# 🧛‍♀️🤖 Telegram Persona AI Bot Engine 💁‍♀️🧚‍♀️

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

> A simple, lightweight, and production-ready Telegram AI persona bot engine powered by **aiogram 3**, **OpenAI / OpenRouter API**, and **PostgreSQL**.

Pesona AI Bot is designed with a **configuration-first approach**: it acts as a clean, bot-agnostic template. All personality traits, system prompts, and responses are completely decoupled from the codebase, allowing you to deploy custom AI characters or assistants in minutes without altering a single line of Python code.

---

##  Features

- **⚡ Simple Setup**: Fire up a fully functioning AI bot in seconds using Docker Compose.
- **🎭 Bot-Agnostic & Config-Driven**: Change the bot's name, system prompt, and starting messages via simple `config.json` and `persona.txt` files.
- **🧠 Long-Term Memory**: Stores conversation history per user in PostgreSQL using SQLAlchemy 2.0.
- **🔒 Privacy-First**: Keeps private persona data and secrets out of the repository using `.env` environment variables.

---

##  Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/sanchexas/persona-ai-bot
cd persona-ai-bot
```
### 2. Configure Environment & Persona  
- Copy the example files to create your custom configuration:
```bash
cp .env.example .env
cp config.json.example config.json
cp persona.txt.example persona.txt
```
- Fill in your API keys in ```.env``` (```TG_BOT_TOKEN```, ```OPENROUTER_API_KEY```, etc.).

- Adjust starting messages in config.json.

- Write your character's system prompt in persona.txt.

### 3. Launch with Docker Compose
Run the simple build command to launch both the bot and PostgreSQL database:
```bash
docker compose up -d --build
```
That's it! Your AI bot is live and listening.

### Management commands
- Reset database & start fresh (clears chat history):
```bash
docker compose down -v
docker compose up -d --build
```

##  License

This project is open-source and available under the [MIT License](LICENSE).