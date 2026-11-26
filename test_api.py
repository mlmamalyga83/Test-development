import unittest
import os
import requests
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# Задача №2: Автотест API Яндекс.Диска
# Проверяем создание папки через REST API
# ============================================================

class TestYandexDiskAPI(unittest.TestCase):
    """Тесты для Яндекс.Диск REST API"""

    BASE_URL = "https://cloud-api.yandex.net/v1/disk/resources"

    @classmethod
    def setUpClass(cls):
        cls.token = os.getenv("YA_DISK_TOKEN")
        cls.folder_name = "test_folder_api"
        cls.headers = {}
        if cls.token:
            cls.headers = {"Authorization": f"OAuth {cls.token}"}

    def setUp(self):
        # удаляем папку если осталась от прошлого теста
        if self.token:
            requests.delete(
                self.BASE_URL,
                headers=self.headers,
                params={"path": self.folder_name}
            )

    def tearDown(self):
        # удаляем созданную папку после теста
        if self.token:
            requests.delete(
                self.BASE_URL,
                headers=self.headers,
                params={"path": self.folder_name}
            )

    def test_create_folder_success(self):
        """Создание папки — должен быть код 201"""
        if not self.token:
            self.skipTest("Нет токена YA_DISK_TOKEN")

        response = requests.put(
            self.BASE_URL,
            headers=self.headers,
            params={"path": self.folder_name}
        )
        self.assertEqual(response.status_code, 201,
                         f"Ожидался 201, получен {response.status_code}")

    def test_folder_in_list(self):
        """После создания папка отображается в списке файлов"""
        if not self.token:
            self.skipTest("Нет токена YA_DISK_TOKEN")

        # создаём папку
        requests.put(
            self.BASE_URL,
            headers=self.headers,
            params={"path": self.folder_name}
        )

        # получаем список файлов в корне
        response = requests.get(
            self.BASE_URL,
            headers=self.headers,
            params={"path": "/"}
        )
        self.assertEqual(response.status_code, 200)

        items = response.json().get("_embedded", {}).get("items", [])
        folder_names = [item["name"] for item in items]
        self.assertIn(self.folder_name, folder_names,
                      f"Папка {self.folder_name} не найдена в списке")

    def test_create_existing_folder(self):
        """Повторное создание той же папки — код 409"""
        if not self.token:
            self.skipTest("Нет токена YA_DISK_TOKEN")

        # первый раз — ок
        requests.put(
            self.BASE_URL,
            headers=self.headers,
            params={"path": self.folder_name}
        )

        # второй раз — ошибка 409
        response = requests.put(
            self.BASE_URL,
            headers=self.headers,
            params={"path": self.folder_name}
        )
        self.assertEqual(response.status_code, 409,
                         f"Ожидался 409, получен {response.status_code}")

    def test_create_folder_no_auth(self):
        """Запрос без токена — код 401"""
        response = requests.put(
            self.BASE_URL,
            params={"path": self.folder_name}
        )
        self.assertEqual(response.status_code, 401,
                         f"Ожидался 401, получен {response.status_code}")

    def test_create_folder_invalid_name(self):
        """Недопустимое имя папки — код 400"""
        if not self.token:
            self.skipTest("Нет токена YA_DISK_TOKEN")

        response = requests.put(
            self.BASE_URL,
            headers=self.headers,
            params={"path": "//invalid//name//"}
        )
        self.assertEqual(response.status_code, 400,
                         f"Ожидался 400, получен {response.status_code}")

    def test_folder_metadata(self):
        """Проверка метаинформации созданной папки"""
        if not self.token:
            self.skipTest("Нет токена YA_DISK_TOKEN")

        requests.put(
            self.BASE_URL,
            headers=self.headers,
            params={"path": self.folder_name}
        )

        response = requests.get(
            self.BASE_URL,
            headers=self.headers,
            params={"path": self.folder_name}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], self.folder_name)
        self.assertEqual(response.json()["type"], "dir")

    def test_delete_folder(self):
        """Удаление созданной папки — код 204"""
        if not self.token:
            self.skipTest("Нет токена YA_DISK_TOKEN")

        requests.put(
            self.BASE_URL,
            headers=self.headers,
            params={"path": self.folder_name}
        )

        response = requests.delete(
            self.BASE_URL,
            headers=self.headers,
            params={"path": self.folder_name}
        )
        self.assertEqual(response.status_code, 204,
                         f"Ожидался 204, получен {response.status_code}")

    def test_delete_nonexistent_folder(self):
        """Удаление несуществующей папки — код 404"""
        if not self.token:
            self.skipTest("Нет токена YA_DISK_TOKEN")

        response = requests.delete(
            self.BASE_URL,
            headers=self.headers,
            params={"path": "folder_that_does_not_exist_12345"}
        )
        self.assertEqual(response.status_code, 404,
                         f"Ожидался 404, получен {response.status_code}")


if __name__ == '__main__':
    unittest.main()