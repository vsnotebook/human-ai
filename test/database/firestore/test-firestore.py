import os
import time
import uuid
from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore import Client

from src.config.plans import SUBSCRIPTION_PLANS
# from src.config.payment_config import SUBSCRIPTION_PLANS
from src.constants import PROJECT_ID

os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"

db: Client = firestore.Client(project=PROJECT_ID)

## firestore 不需要创建表。可以直接插入就会同时创建一张表。

def create_test_tbl(user_id: str, plan_id: str):
    start_time = time.time()  # 记录开始时间
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
    end_time = time.time()  # 记录结束时间
    execution_time = end_time - start_time  # 计算执行时间
    print(f"程序执行时间: {execution_time:.2f} 秒")

    return test_tbl_data


def test_query():
    start_time = time.time()
    try:
        # 条件查询
        print("\n条件查询结果:")
        query = db.collection('test_tbl').where('status', '==', 'pending').limit(5)
        docs = query.stream()
        for doc in docs:
            data = doc.to_dict()
            print(f"订单ID: {data['id']}, 计划: {data['plan_name']}, 金额: {data['amount']}")


    except Exception as e:
        print(f"查询出错: {e}")
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\n程序执行时间: {execution_time:.2f} 秒")


def test_query2():
    start_time = time.time()
    try:
        # 查询单个文档
        doc_ref = db.collection('test_tbl').document('1')
        doc = doc_ref.get()
        if doc.exists:
            print("单个文档查询结果:")
            print(doc.to_dict())
        else:
            print("文档不存在")

        # 条件查询
        print("\n条件查询结果:")
        query = db.collection('test_tbl').where('status', '==', 'pending').limit(5)
        docs = query.stream()
        for doc in docs:
            data = doc.to_dict()
            print(f"订单ID: {data['id']}, 计划: {data['plan_name']}, 金额: {data['amount']}")

        # 按创建时间排序查询
        print("\n按时间排序的查询结果:")
        query = db.collection('test_tbl').order_by('created_at', direction=firestore.Query.DESCENDING).limit(3)
        docs = query.stream()
        for doc in docs:
            data = doc.to_dict()
            print(f"订单ID: {data['id']}, 创建时间: {data['created_at']}")

        # 复合查询
        print("\n复合查询结果:")
        query = (db.collection('test_tbl')
                .where('amount', '>', 0)
                .where('status', '==', 'pending')
                .order_by('amount')
                .limit(5))
        docs = query.stream()
        for doc in docs:
            data = doc.to_dict()
            print(f"订单ID: {data['id']}, 计划: {data['plan_name']}, 金额: {data['amount']}")

    except Exception as e:
        print(f"查询出错: {e}")
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\n程序执行时间: {execution_time:.2f} 秒")


# 在文件末尾添加测试调用
if __name__ == "__main__":
    # create_test_tbl("1122334455", "enterprise")
    test_query()
