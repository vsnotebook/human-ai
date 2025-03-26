import os

# Google Cloud Speech-to-Text v2 setup
PROJECT_ID = "human-ai-454609"
# REGION = "global"
CREDENTIALS_PATH = "human-ai-454609-bf84b910d612.json"

# Proxy settings
# os.environ["http_proxy"] = "http://127.0.0.1:7897"
# os.environ["https_proxy"] = "http://127.0.0.1:7897"

# os.environ["http_proxy"] = "http://127.0.0.1:10808"
# os.environ["https_proxy"] = "http://127.0.0.1:10808"

# Server settings
SERVER_HOST = "0.0.0.0"
# SERVER_HOST = "127.0.0.1"
SERVER_PORT = int(os.environ.get("PORT", 8085))


