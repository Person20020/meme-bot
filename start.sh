#!/bin/bash
. ~/meme-bot/venv/bin/activate
cd ~/meme-bot/app
exec gunicorn -w 1 -b 127.0.0.1:3003 app:app --access-logfile ~/meme-bot/logs/access.log --error-logfile ~/meme-bot/logs/error.log