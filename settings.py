import os
import sys

from dotenv import load_dotenv
load_dotenv()

teams_token = os.getenv("TEAMS_BOT_TOKEN", "")
room_id = os.getenv("TEAMS_ROOM_ID", "")

try:
    assert teams_token
    assert room_id
except AssertionError:
    print("AssertionError: Unable to get value for environment variables: [TEAMS_BOT_TOKEN, TEAMS_ROOM_ID]")
    sys.exit(2)

if __name__ == '__main__':
    print(teams_token, room_id)
