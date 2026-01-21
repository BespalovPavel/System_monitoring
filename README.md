# System_monitoring

This is a Python monitoring script that collects metrics (CPU, RAM, disks) and 
sends alerts to Telegram when thresholds are exceeded. 
Using the /status command in the bot, you can find out the current metrics.<br>

The data will be stored locally in a folder./monitor_data and on the container in /app/data/monitor.db

# Quick start

It is necessary to fill in .env (to do this, create a bot in Telegram)<br>
then:<br>

pip install -r requirements.txt<br>
docker compose down<br>
docker compose up -d --build<br>
docker compose logs -f<br>

# Enjoy

use a bot

