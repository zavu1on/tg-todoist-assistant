# 🤖 Todoist AI Assistant Bot

**AI-powered Telegram bot for managing your tasks in Todoist**

This bot allows you to **add**, **view**, and **organize** your Todoist tasks directly from Telegram. It leverages the **Todoist API** for task management and integrates **LLM models via OpenRouter** to enhance task descriptions and generate smart suggestions.

---

## 🚀 Features

- 📌 Add tasks with natural language
- 🗓️ Automatically parse dates and times
- 🧠 Use AI to rephrase and clarify task descriptions
- 🔁 OAuth authentication with Todoist
- 💬 Simple, intuitive Telegram interface

---

## ⚙️ Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/zavu1on/tg-todoist-assistant.git
cd tg-todoist-assistant
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate         # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Telegram Bot
BOT_TOKEN=                      # Telegram API token from @BotFather
DB_PATH=users.db               # Path to your SQLite database file

# Todoist OAuth
TODOIST_CLIENT_ID=             # Your Todoist OAuth App Client ID
TODOIST_CLIENT_SECRET=         # Your Todoist OAuth App Client Secret

# LLM (OpenRouter)
OPENROUTER_API_KEY=            # Your OpenRouter API key
MODEL=mistralai/mistral-nemo:free # Default model to use
```

---

## ▶️ Running the Bot

Make sure your environment is set up:

```bash
source venv/bin/activate        # Or venv\Scripts\activate on Windows
python main.py
```

---

## 🛠 Deployment Notes

For persistent deployments in production environments:

* Use a **process manager** like `systemd`, `supervisord`, or `pm2`
* Or run inside **Docker** for containerized management

---

## 📄 License

MIT License. See [`LICENSE`](./LICENSE) for details.
