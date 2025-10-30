import random
import time
from collections import OrderedDict


# Клас LRU-кешу
class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


# Функції без кешу
def range_sum_no_cache(array, left, right):
    return sum(array[left:right + 1])


def update_no_cache(array, index, value):
    array[index] = value


# Функції з кешем
cache = LRUCache(1000)

def range_sum_with_cache(array, left, right):
    key = (left, right)
    result = cache.get(key)
    if result == -1:  # cache-miss
        result = sum(array[left:right + 1])
        cache.put(key, result)
    return result


def update_with_cache(array, index, value):
    array[index] = value
    # Інвалідація кешу (видаляємо ключі, що охоплюють змінений елемент)
    keys_to_delete = [k for k in cache.cache.keys() if k[0] <= index <= k[1]]
    for k in keys_to_delete:
        del cache.cache[k]


# Генерація запитів
def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:  # ~3% запитів — Update
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:  # ~97% — Range
            if random.random() < p_hot:  # 95% — «гарячі» діапазоних
                left, right = random.choice(hot)
            else:   # 5% — випадкові діапазони
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries


# Тестування
def run_test():
    n = 100_000
    q = 50_000
    array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    # Без кешу
    start = time.time()
    for query in queries:
        if query[0] == "Range":
            range_sum_no_cache(array, query[1], query[2])
        else:
            update_no_cache(array, query[1], query[2])
    t_no_cache = time.time() - start

    # З кешем
    global cache
    cache = LRUCache(1000)
    start = time.time()
    for query in queries:
        if query[0] == "Range":
            range_sum_with_cache(array, query[1], query[2])
        else:
            update_with_cache(array, query[1], query[2])
    t_cache = time.time() - start

    # Вивід результатів
    print(f"Без кешу : {t_no_cache:.2f} c")
    print(f"LRU-кеш  : {t_cache:.2f} c  (прискорення ×{t_no_cache / t_cache:.1f})")


if __name__ == "__main__":
    run_test()
