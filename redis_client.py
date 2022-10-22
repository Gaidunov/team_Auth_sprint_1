# python shell
import redis


class RedisCli:
    def __init__(self) -> None:
        self = redis.Redis(host='localhost', port=6379, db=0)

redis_cli = redis.Redis(host='localhost', port=6379, db=0)


# def set_two_factor_auth_code(pipeline: redis.client.Pipeline) -> None:
#     pipeline.setex('key', 10, 'value')
#     pipeline.setex('key2', 10, 'value')
#     pipeline.setex('key3', 10, 'value')
#     pipeline.setex('key4', 10, 'value')

# redis_db.transaction(set_two_factor_auth_code) 
# redis_db.get('key')  # Получить значение по ключу
# redis_db.set('key', 'value')  # Положить значение по ключу
# redis_db.expire('key', 10)  # Установить время жизни ключа в секундах
# # А можно последние две операции сделать за один запрос к Redis.
# redis_db.setex('key', 10, 'value')  # Положить значение по ключу с ограничением времени 