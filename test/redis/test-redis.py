"""Basic connection example.
"""

# redis-cli -u redis://default:pUoxbvYw6mM6Yc7eg7x4WnkhyXhDznvG@redis-12842.c1.asia-northeast1-1.gce.redns.redis-cloud.com:12842
import redis

r = redis.Redis(
    host='redis-12842.c1.asia-northeast1-1.gce.redns.redis-cloud.com',
    port=12842,
    decode_responses=True,
    username="default",
    password="pUoxbvYw6mM6Yc7eg7x4WnkhyXhDznvG",
)

success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
# >>> bar

