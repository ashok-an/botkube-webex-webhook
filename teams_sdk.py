import json
from webexteamssdk import WebexTeamsAPI
import settings

api = WebexTeamsAPI(access_token=settings.teams_token)

def get_me():
    return api.people.me()

def send_message_to_user(user_id, message):
    toEmail = user_id + '@cisco.com'
    api.messages.create(toPersonEmail=toEmail, markdown=message, files=["https://www.webex.com/content/dam/wbx/us/images/dg-integ/teams_icon.png"])
    return

def send_message_to_room(room_id, message):
    api.messages.create(roomId=room_id, markdown=message)
    return

def _wrap(card_obj):
    return {"contentType": "application/vnd.microsoft.card.adaptive", "content": card_obj.to_dict()}

def send_card_to_user(user_id, card_obj, fallback_message='card creation failed'):
    toEmail = user_id + '@cisco.com'
    api.messages.create(toPersonEmail=toEmail, attachments=[card_obj,], text=fallback_message)
    return

def send_card_to_room(room_id, card_obj, fallback_message='card creation failed'):
    api.messages.create(roomId=room_id, attachments=[card_obj,], text=fallback_message)
    return

def create_card(title, cluster, namespace, message):
    _json = {"contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.0",
            "msteams": {
                "width": "Full"
            },
            "body": [{'type': 'RichTextBlock', 'inlines': [{'type': 'TextRun', 'color': 'accent', 'text': title,
                'size': 'medium'}], 'separator': True}],
            }
        }
    factSet = {"type": "FactSet", "facts": []}
    factSet['facts'].append({'title': 'Cluster', 'value': cluster})
    factSet['facts'].append({'title': 'Namespace', 'value': namespace})
    factSet['facts'].append({'title': 'Details', 'value': message})
    _json['content']['body'].append(factSet)


    #print("Message: {}".format(json.dumps(_json, sort_keys=True, indent=4)), flush=True)
    return _json

if __name__ == '__main__':
    print(get_me())
