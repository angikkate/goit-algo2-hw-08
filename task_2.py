import random
import time
from typing import Dict
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_windows: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        # Видаляє старі повідомлення поза межами вікна
        if user_id not in self.user_windows:
            return

        window = self.user_windows[user_id]
        while window and (current_time - window[0]) > self.window_size:
            window.popleft()

        # Якщо у користувача більше немає записів — видаляємо ключ
        if not window:
            del self.user_windows[user_id]

    def can_send_message(self, user_id: str) -> bool:
        # Перевіряє, чи можна відправити повідомлення зараз
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_windows:
            return True

        return len(self.user_windows[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        # Реєструє повідомлення, якщо можливо
        current_time = time.time()
        if self.can_send_message(user_id):
            if user_id not in self.user_windows:
                self.user_windows[user_id] = deque()
            self.user_windows[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        # Обчислює, через скільки секунд можна надіслати наступне повідомлення
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_windows:
            return 0.0

        window = self.user_windows[user_id]
        if len(window) < self.max_requests:
            return 0.0

        # Час, коли перше повідомлення у вікні стане "старим"
        return max(0.0, self.window_size - (current_time - window[0]))


# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)
    
    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        
        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
