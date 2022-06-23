import json
import logging
import os
import re
import sys

from flask import Flask, request, jsonify
from tabulate import tabulate

from flask import has_request_context, request
from flask.logging import default_handler

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
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n\t'
    '%(levelname)s in %(module)s: %(message)s'
)
default_handler.setFormatter(formatter)
default_handler.setLevel(logging.INFO)

app = Flask(__name__)

def get_room_mapping(lookup_dir="/tmp/lookup_table"):
    try:
        sys.path.append(lookup_dir)
        import lookup_table
        return lookup_table.room_mapping
    except Exception as e:
        print(f"Exception: get_room_mapping failed; error : {e}")
        sys.exit(3)

def get_room_id(namespace):
    mapping = get_room_mapping()
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
#        app.logger.info("+ payload: {}".format(json.dumps(_json, indent=4, sort_keys=True)))

        cluster = _json.get('meta', {}).get('cluster', 'no-cluster')
        namespace = _json.get('meta', {}).get('namespace', 'no-namespace')
        kind = _json.get('meta', {}).get('kind', 'no-kind')
        name = _json.get('meta', {}).get('name', 'no-name')
        title = f" 🚩 {kind}/{name}"

        status = _json.get('status', {})
        status_type = status.get('type', 'no-type')

        details = _json.get("summary", "") if "summary" in _json else ""
        details = status.get("messages", [])[0] if "messages" in status else ""

        fallback_message = f"{cluster}/{namespace}/{title} - {details}"

        if status_type == 'error':
            room_id = get_room_id(namespace)
            if room_id:
                card = teams_sdk.create_card(title, cluster, namespace, details)
                teams_sdk.send_card_to_room(room_id, card, fallback_message)
            else:
                app.logger.error(f"No mapping found for namespace:{namespace}")
            app.logger.info(f"Notifying event-type:{status} for namespace:{namespace}")
        else:
            app.logger.warning(f"Ignored event-type:{status_type} for namespace:{namespace}")
        return jsonify("Webhook received!")

    else:
        app.logger.info("{} method called; returning OK".format(request.method))
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
    app.logger.setLevel(logging.INFO)
    app.run(host='0.0.0.0', port=8000, debug=False)
