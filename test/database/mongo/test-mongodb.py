# python -m pip install "pymongo[srv]"
import os
import time

import bcrypt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# os.environ["http_proxy"] = "http://127.0.0.1:10808"
# os.environ["https_proxy"] = "http://127.0.0.1:10808"
uri = "mongodb+srv://vswork666:VuSnbgmkrs4jamVt@cluster0.naywsqs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


def test_insert():
    start_time = time.time()  # 记录开始时间

    # Create a new client and connect to the server
    client: MongoClient = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        db = client.web
        users_ref = db.users

        # 使用bcrypt加密密码
        password_hash = bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt())

        # 创建用户文档
        users_ref.insert_one({
            'username': "vsfran",
            'email': "vsfran@qq.com",
            'password_hash': password_hash,
            'role': "user",
            'trial_count': 10,
            'trial_seconds': 60,
            'created_at': time.time()
        })

    except Exception as e:
        print(e)
    finally:
        end_time = time.time()  # 记录结束时间
        execution_time = end_time - start_time  # 计算执行时间
        print(f"程序执行时间: {execution_time:.2f} 秒")


def test_query(client, username):
    start_time = time.time()
    # db.users.create_index("username", unique=True)
    # db.users.create_index("last_try")
    # client: MongoClient = MongoClient(uri, server_api=ServerApi('1'))
    try:
        db = client.web
        users_ref = db.users

        # 查询单个用户
        user = users_ref.find_one({'username': username})
        if user:
            print("找到用户:")
            print(f"用户名: {user['username']}")
            print(f"邮箱: {user['email']}")
            print(f"角色: {user['role']}")
            print(f"试用次数: {user['trial_count']}")
        else:
            print("未找到用户")

        # 查询所有用户
        # print("\n所有用户列表:")
        # all_users = users_ref.find()
        # for user in all_users:
        #     print(f"用户名: {user['username']}, 邮箱: {user['email']}")

    except Exception as e:
        print(e)
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\n程序执行时间: {execution_time:.2f} 秒")


def test_advanced_query():
    start_time = time.time()

    client: MongoClient = MongoClient(uri, server_api=ServerApi('1'))
    try:
        db = client.web
        users_ref = db.users

        # 条件查询：查找试用次数大于5的用户
        print("查找试用次数大于5的用户:")
        users = users_ref.find({"trial_count": {"$gt": 5}}).sort("created_at", -1).limit(5)
        for user in users:
            print(f"用户名: {user['username']}, 试用次数: {user['trial_count']}")

        # 统计查询
        total_users = users_ref.count_documents({})
        admin_users = users_ref.count_documents({"role": "user"})
        print(f"\n统计信息:")
        print(f"总用户数: {total_users}")
        print(f"普通用户数: {admin_users}")

        # 聚合查询：按角色分组统计用户数
        pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]
        role_stats = users_ref.aggregate(pipeline)
        print("\n用户角色统计:")
        for stat in role_stats:
            print(f"角色: {stat['_id']}, 数量: {stat['count']}")

    except Exception as e:
        print(f"查询出错: {e}")
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\n程序执行时间: {execution_time:.2f} 秒")


def test_query_many():
    client: MongoClient = MongoClient(uri, server_api=ServerApi('1'))
    test_query(client, 'vsfran')
    print("=========================")
    test_query(client, 'liu2')
    print("=========================")
    test_query(client, 'liu1')
    print("=========================")
    test_query(client, 'liu555')
    print("=========================")


# 在文件末尾添加测试调用
if __name__ == "__main__":
    # test_insert()
    test_query_many()
    # test_advanced_query()
