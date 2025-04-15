# 🤖 Telegram Bot on AWS EC2

[👉 Funny Quiz Bot](https://t.me/Funny_quiz_ledeneva_bot)

This project is a simple Telegram bot deployed on an Amazon EC2 instance running Amazon Linux 2023. The bot is written in Python and managed with a minimal deployment setup using GitHub Actions.

## 🧩 Project Overview

- **Language**: Python 3
- **Platform**: Amazon EC2 (Amazon Linux 2023)
- **Deployment**: GitHub Actions
- **Bot Start Command**: `nohup python3 test.py > test.log 2>&1 &`
  
## 🔧 Technologies Used

- **Python** — for writing the Telegram bot logic.
- **Amazon EC2** — for hosting and running the bot.
- **GitHub Actions** — for updating the bot script remotely after code changes.
- **SSH + PEM Key** — for secure access to the EC2 instance.
- **nohup** — for running the bot in the background and capturing logs.
- **scp / ssh** — for transferring files and restarting the bot.
