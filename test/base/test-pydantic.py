from pydantic import BaseModel, HttpUrl, ValidationError, RedisDsn
from typing import Optional


class MyModel(BaseModel):
    url: Optional[HttpUrl] = None
    redis_url: Optional[RedisDsn]


m = MyModel(url='http://www.example.com', redis_url='rediss://:pass@localhost')
print(m.url)
# > http://www.example.com/

try:
    MyModel(url='ftp://invalid.url')
    print("=====================1")
except ValidationError as e:
    print("111111111111111111111111111111")
    print(e)
    '''
    1 validation error for MyModel
    url
      URL scheme should be 'http' or 'https' [type=url_scheme, input_value='ftp://invalid.url', input_type=str]
    '''

try:
    MyModel(url='not a url')
    print("=====================2")
except ValidationError as e:
    print("2222222222222222222222222222222222222222222")
    print(e)
    '''
    1 validation error for MyModel
    url
      Input should be a valid URL, relative URL without a base [type=url_parsing, input_value='not a url', input_type=str]
    '''

a = MyModel(redis_url='rediss://:pass@localhost')
print(a.redis_url)
