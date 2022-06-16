import json
from flask import Flask, request, jsonify
from tabulate import tabulate
import teams_sdk
import settings

app = Flask(__name__)

def format_json_to_markdown(_json):
    meta = _json.get('meta', {})
    status = _json.get('status', {})
    if not (meta and status):
        return {}

    what = f"{meta['cluster']}/{meta['namespace']}/{meta['name']}"

    summary = _json.get("summary", "") if "summary" in _json else ""
    summary = status.get("messages", [])[0] if "messages" in status else ""

    output = tabulate([['Object Ref.', what], ['Event type', f"{meta['kind']}.{status['type']}"], ['Details', summary]],
                headers=[], tablefmt="presto")
    return output


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # print("+ payload: {}".format(json.dumps(request.json, indent=4, sort_keys=True)))
        message = format_json_to_markdown(request.json)
        teams_sdk.send_message_to_room(settings.room_id, "```json\n{}\n```".format(message))
        return jsonify("Webhook received!")

    else:
        print("{} method called; returning OK".format(request.method))
        return "{} OK".format(request.method)

@app.route("/", methods=['GET'])
def home():
    return jsonify({"message": "POST to /webhook"})

@app.route("/ping", methods=['GET'])
def ping():
    return jsonify({"message": "pong"})

@app.route("/healthz", methods=['GET'])
def health():
    return jsonify({"health": "OK"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
