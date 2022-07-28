import json
import logging
import os
import re
import sys

from flask import Flask, request, jsonify
from flask import has_request_context, request
from flask.logging import default_handler
import re

from faker import Faker
fake = Faker()

from tabulate import tabulate

import teams_sdk
import settings

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s | %(url)s\n + '
    '%(levelname)s - %(message)s'
)
default_handler.setFormatter(formatter)
default_handler.setLevel(logging.INFO)

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
logging.basicConfig(filename='record.log', level=logging.WARNING, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def get_room_mapping(json_path="/tmp/lookup_table/mapping.json"):
    try:
        with open(json_path, 'r') as fp:
            return json.load(fp)
    except Exception as e:
        print(f"Exception: get_room_mapping failed; error: {e}")
        sys.exit(3)

# need to do this once else api call times out
mapping = get_room_mapping()

def get_room_id(namespace):
    for k, v in mapping.items():
        m = re.search(k, namespace, re.IGNORECASE)
        if m and m.group(0):
            return v
        # endif
    else:
        return mapping.get('default-case', '')

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        _json = request.json
        app.logger.info("+ payload: {}".format(json.dumps(_json, sort_keys=True)))

        cluster = _json.get('meta', {}).get('cluster', 'no-cluster')
        namespace = _json.get('meta', {}).get('namespace', 'no-namespace')
        kind = _json.get('meta', {}).get('kind', 'no-kind')
        name = _json.get('meta', {}).get('name', 'no-name')

        status = _json.get('status', {})
        status_type = status.get('type', 'no-type')
        status_level = status.get('level', 'no-level')

        details = _json.get("summary", "") if "summary" in _json else ""
        details = status.get("messages", [])[0] if "messages" in status else ""
        check_liveness = re.match("Liveness probe failed: Get \".*\": context deadline exceeded", details)
        check_readiness = re.match("Readiness probe failed: Get \".*\": context deadline exceeded", details)

        timestamp = _json.get("timestamp", "")
        if details == "Liveness prob failed:" or details == "Readiness probe failed:":
            app.logger.error (f"Ignoted payload: {details}")
        elif check_liveness or check_readiness:
            app.logger.error(f"Ignoted payload: {details}")
        elif status_level == 'critical' or status_type == 'error':
            room_id = get_room_id(namespace)
            app.logger.warning(f"Notifying event-type:{status} for namespace:{namespace} to roomId:{room_id}")
            if room_id:
                pre = f"🚩 Error in {kind}/{name}"
                app.logger.warning(f"Sending notification for {kind}/{name} ...")
                card = teams_sdk.create_card(pre, cluster, namespace, timestamp, details)
                teams_sdk.send_card_to_room(room_id, card, f"Error in {cluster}/{namespace}/{kind}/{name} - {details}")
            else:
                app.logger.error(f"No mapping found for namespace:{namespace}")
        else:
            app.logger.warning(f"Ignored event-type:{status_type} for namespace:{namespace}")
        return jsonify("Webhook received!")

    else:
        app.logger.info("{} method called; returning OK".format(request.method))
        return "{} OK".format(request.method)

@app.route("/", methods=['GET'])
def home():
    return jsonify({"message": "POST to /webhook"})

@app.route("/test/<user>", methods=['GET'])
def test(user):
    table = tabulate([['User', fake.name()], ['Message', fake.text()[:80]]], tablefmt="presto")
    teams_sdk.send_message_to_user(user, f"```\n{table}\n```")
    return jsonify({"message": f"sent message to {user}"})

@app.route("/ping", methods=['GET'])
def ping():
    return jsonify({"message": "pong"})

@app.route("/healthz", methods=['GET'])
def health():
    return jsonify({"health": "OK"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
