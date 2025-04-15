# 🚀 Telegram Bot Autodeploy on AWS EC2

This project demonstrates how to automatically deploy a Telegram bot to an Amazon EC2 instance using GitHub Actions.

## 📁 Structure

- `test.py` — Main Telegram bot script.
- `.github/workflows/deploy.yml` — GitHub Actions workflow for automated deployment.
- `README.md` — Project description.

## ⚙️ How It Works

Whenever you push to the `main` branch and `test.py` is modified:

1. **GitHub Actions**:
   - Reads the `test.py` file.
   - Connects to your EC2 instance over SSH.
   - Uploads the file to the server.
   - Stops the currently running bot process (if any).
   - Starts a new process using `nohup`.

2. **Amazon EC2**:
   - Runs on Amazon Linux 2023.
   - Runs Python 3.
   - The bot runs in the background, and logs are saved to `test.log`.
