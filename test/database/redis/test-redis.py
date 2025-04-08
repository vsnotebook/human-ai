import time

import redis

r = redis.Redis(
  host='assured-orca-63378.upstash.io',
  port=6379,
  password='AfeSAAIjcDFjN2FjM2NlZjJiYjU0Njg4Yjg5MDRiZjBhMjZhMzU5ZnAxMA',
  ssl=True
)
start_time = time.time()
r.set('foo', 'bar')
print(r.get('foo'))

print(f"\n程序执行时间: {time.time() - start_time:.2f} 秒")
start_time1 = time.time()
print(r.get('foo'))
print(f"\n程序执行时间: {time.time() - start_time1:.2f} 秒")

