import os
import uuid
from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore import Client

from config.plans import SUBSCRIPTION_PLANS
from env import PROJECT_ID

os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"

db: Client = firestore.Client(project=PROJECT_ID)

## firestore 不需要创建表。可以直接插入就会同时创建一张表。

def create_test_tbl(user_id: str, plan_id: str):
    plan = SUBSCRIPTION_PLANS[plan_id]
    order_id = str(uuid.uuid4())

    test_tbl_data = {
        'id': order_id,
        'user_id': user_id,
        'plan_id': plan_id,
        'plan_name': plan['name'],
        'amount': plan['price'],
        'minutes': plan['minutes'],
        'duration': plan['duration'],
        'status': 'pending',
        'created_at': datetime.now()
    }

    # 保存订单到 Firestore
    db.collection('test_tbl').document(order_id).set(test_tbl_data)

    return test_tbl_data


create_test_tbl("1122334455", "enterprise")
