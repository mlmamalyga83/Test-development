import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# Задача №3 (дополнительная): Selenium — авторизация на Яндексе
# ============================================================

class TestYandexPassportAuth(unittest.TestCase):
    """Тесты для страницы авторизации Яндекса"""

    URL = "https://passport.yandex.ru/auth/"

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_page_loads(self):
        """Страница авторизации загружается без ошибок"""
        self.driver.get(self.URL)
        title = self.driver.title
        self.assertIn("Авторизация", title)

    def test_login_input_exists(self):
        """На странице есть поле ввода логина"""
        self.driver.get(self.URL)
        login_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "passp-field-login"))
        )
        self.assertTrue(login_input.is_displayed())

    def test_submit_button_exists(self):
        """На странице есть кнопка 'Войти'"""
        self.driver.get(self.URL)
        button = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@type='submit']")
            )
        )
        self.assertTrue(button.is_displayed())

    def test_incorrect_login_shows_error(self):
        """Ввод невалидного логина — появляется сообщение об ошибке"""
        self.driver.get(self.URL)

        login_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "passp-field-login"))
        )
        login_input.send_keys("this_login_definitely_does_not_exist_12345")

        submit_button = self.driver.find_element(
            By.XPATH, "//button[@type='submit']"
        )
        submit_button.click()

        # ждём появления сообщения об ошибке
        error = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'Textinput-Hint_state_error')]")
            )
        )
        self.assertTrue(error.is_displayed())


if __name__ == '__main__':
    unittest.main()