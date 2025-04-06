import os

from google.cloud.speech_v2 import SpeechClient
from google.cloud.location import locations_pb2
from google.protobuf.json_format import MessageToDict

PROJECT_ID = "human-ai-454609"

os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"


def list_locations():
    client = SpeechClient()

    request = locations_pb2.ListLocationsRequest(
        name=f"projects/{PROJECT_ID}"
    )

    response = client.list_locations(request=request)

    for location in response.locations:
        # 将 protobuf 消息转换为字典格式，便于读取
        location_dict = MessageToDict(location)
        print(f"\n位置 ID: {location_dict.get('locationId')}")
        print(f"显示名称: {location_dict.get('displayName')}")
        print(f"元数据: {location_dict.get('metadata', {})}")
        print("---")

    return response

list_locations()
