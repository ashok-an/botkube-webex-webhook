# botkube-webex-webhook
Webhook handler for sending events from botkube to webex teams

# How to build
`docker build -t <whatever-tag> .`

# How to run
`docker run [-d] -e TEAMS_BOT_TOKEN=<teams-token> -e TEAMS_ROOM_ID=<userId of recepeint> -p 8000:8000 <whatever-tag>`
