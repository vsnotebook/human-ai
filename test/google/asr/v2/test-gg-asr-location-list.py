import os
import json
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
        location_dict = MessageToDict(location)
        print(f"\n位置 ID: {location_dict.get('locationId')}")
        print(f"显示名称: {location_dict.get('displayName')}")
        # print(f"元数据: {location_dict.get('metadata', {})}")
        print("元数据:")
        # 使用 json.dumps 美化输出，indent=2 表示缩进两个空格
        print(json.dumps(location_dict.get('metadata', {}),
                        ensure_ascii=False,
                        indent=2))
        print("---")

    return response


def get_location(location_id):
    client = SpeechClient()

    # 构建位置名称
    location_path = f"projects/{PROJECT_ID}/locations/{location_id}"

    # 创建请求
    request = locations_pb2.GetLocationRequest(
        name=location_path
    )

    # 获取特定位置信息
    location = client.get_location(request=request)

    # 转换为字典并打印
    location_dict = MessageToDict(location)
    print(f"\n位置 ID: {location_dict.get('locationId')}")
    print(f"显示名称: {location_dict.get('displayName')}")
    print("元数据:")
    print(json.dumps(location_dict.get('metadata', {}),
                     ensure_ascii=False,
                     indent=2))

    return location

# list_locations()

# 示例：获取特定位置信息
# 例如获取 asia-southeast1 位置的信息
get_location("asia-southeast1")

