from dotenv import load_dotenv
from flask import Flask, request
import os
from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter
import sqlite3

load_dotenv()
app = Flask(__name__)

slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
slack_signing_secret = os.getenv('SLACK_SIGNING_SECRET')
db_path = os.getenv('DB_PATH', '~/meme-bot/database.db')

if not slack_bot_token:
    raise ValueError("SLACK_BOT_TOKEN environment variable is not set.")

if not slack_signing_secret:
    raise ValueError("SLACK_SIGNING_SECRET environment variable is not set.")

client = WebClient(token=slack_bot_token)
slack_event_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)

# Test database path
try:
    conn = sqlite3.connect(os.path.expanduser(db_path))
    conn.close()
except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")


@app.route('/')
def home():
    return "Check out the home page of the app in Slack!"


slack_event_adapter.on("message")
def handle_message(event_data):
    event = event_data['event']
    if 'subtype' not in event:  # Ignore messages that are not user-generated
        channel_id = event['channel']
        user = event['user']
        text = event['text']
        
        words = text.split()
        if not words:
            return 200

        try:
            conn = sqlite3.connect(os.path.expanduser(db_path))
            cursor = conn.cursor()
            for i in range(len(words)):
                cursor.execute("SELECT response FROM responses WHERE LOWER(keyword) = ?", (words[i].lower(),))
                response = cursor.fetchone()
                if response:
                    response_text = f"Keyword: {words[i]}\nResponse: {response[0]}"
                    client.chat_postMessage(channel=channel_id, text=response_text)
                    conn.close()
                    return 200
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return 500


@app.route('/slack/command')
def handle_commands():
    data = request.form
    command = data.get('command')
    text = data.get('text')
    channel_id = data.get('channel_id')
    user_id = data.get('user_id')
    user = data.get('user_name')

    if command == "/disable-memes":
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM disabled WHERE channel_id = ?", (channel_id,))
        response = cursor.fetchone()
        if response:
            disable_user = response[0]
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=f"The current channel (<{channel_id}>) has already had meme responses disabled by <@{disable_user}>."
            )
        else:
            cursor.execute("INSERT INTO disabled (user_id, channel) VALUES (?, ?)", (user_id, channel_id))
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="You have successfully disabled meme responses for this channel."
            )
            conn.commit()
        conn.close()
        return
    elif command == "/disable-memes-user":
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor
        cursor.execute("SELECT * FROM disabled_users WHERE user_id = ?", (user_id,))
        response = cursor.fetchone()
        if response:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=f"You have already disabled meme responses to you."
            )
        else:
            cursor.execute("INSERT INTO disabled_users (user_id) VALUES (?)", (user_id,))
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="You have successfully disabled meme responses to you."
            )
            conn.commit()
        conn.close()
        return
    else:
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="An unknown command somehow triggered this bot." 
        )
