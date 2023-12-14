import redis, os, json
from datetime import datetime
from app.helpers.functions import get_datetime_now

R = []
for i in range(0,2):
    R.append(redis.Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=i, decode_responses=True))

class Redis():
    def __init__(self, db=0):
        self.db=db
        self.rd = R[db]

    def get(self, key):
        type = self.rd.type(key)
        if type == 'hash':
            return json.loads(self.rd.hget(key, 'data'))
        if type == 'list':
            return self.rd.lrange(key, 0, -1)
        return self.rd.get(key)
    
    def set(self, key, value, ex=None):
        if isinstance(value, dict):
            res = self.rd.hset(key, 'data', json.dumps(value))
        if ex:
            self.rd.expire(f'{key}: data', ex)
            return res
        if isinstance(value, list) or isinstance(value, tuple):
            return self.rd.rpush(key, *value)
        if ex:
            return self.rd.set(key, ex, value)
        return self.rd.set(key, value)
    
    def delete(self, key):
        if not key:
            return 0
        if isinstance(key, list):
            return self.rd.delete(*key)
        return self.rd.delete(key)
    
    def clear(self):
        return self.rd.flushdb()
    
    def keys(self, pattern):
        return self.rd.keys(pattern)
    
    def exists(self, key):
        return self.rd.exists(key)
    