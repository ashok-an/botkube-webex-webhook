import os

from dotenv import load_dotenv
load_dotenv()

bot_email = os.getenv("TEAMS_BOT_EMAIL")
teams_token = os.getenv("TEAMS_BOT_TOKEN")
bot_url = os.getenv("TEAMS_BOT_URL")
bot_app_name = os.getenv("TEAMS_BOT_APP_NAME")
bot_message_to = os.getenv("TEAMS_BOT_MESSAGE_TO")

if __name__ == '__main__':
    print(bot_email, teams_token, bot_url, bot_app_name)
