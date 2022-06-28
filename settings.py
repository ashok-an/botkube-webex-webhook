import os
import sys

teams_token = os.getenv("TEAMS_BOT_TOKEN", "")
try:
    assert teams_token
except AssertionError:
    print("AssertionError: Unable to get value for environment variables: [TEAMS_BOT_TOKEN]")
    sys.exit(2)

if __name__ == '__main__':
    print(teams_token, room_id)
