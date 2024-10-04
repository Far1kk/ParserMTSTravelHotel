import json
import pickle
import time
from WebDriverManager import WebDriverManagerEdge
from config import PATH_COOKIE_MTS
from config import PATH_COOKIE_EXAMPLE
from config import PATH_DRIVER_EDGE
from selenium.webdriver.edge.options import Options as EdgeOprions

class CookieManager:
    def __init__(self, cookie_file_path: str):
        self.cookie_file_path = cookie_file_path

    def load_cookies(self, driver: WebDriverManagerEdge):
        """Загружает куки из файла и добавляет их в текущий сеанс драйвера."""
        try:
            cookies = pickle.load(open(self.cookie_file_path, "rb"))
            for cookie in cookies:
                driver.driver.add_cookie(cookie)
            print('Куки загружены в драйвер')
        except FileNotFoundError:
            print("Файл с куками не найден.")
        except json.JSONDecodeError:
            print("Ошибка при загрузке куков из файла.")
        except Exception as e:
            print('Ошибка: ', e)

    def save_cookies(self, driver: WebDriverManagerEdge, auth_url: str):
        """Сохраняет куки текущего сеанса драйвера в файл."""
        driver.driver.execute_script(f"window.open('{auth_url}', '_blank');")
        time.sleep(5)
        current_window = driver.driver.current_window_handle
        driver.driver.switch_to.window(current_window)
        pickle.dump(driver.driver.get_cookies(), open(self.cookie_file_path, "wb"))
        print('Куки успешно сохранены в ', self.cookie_file_path)

# Пример использования
if __name__ == "__main__":
    cookie_file_path = PATH_COOKIE_EXAMPLE

    options = EdgeOprions()
    options.use_chromium = True  # Использование Chromium-совместимую версию Edge
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')  # Отключение опции автоматизированного ПО
    options.add_argument("--disable-extensions")  # Отключение опции расширений
    options.add_argument("--disable-webgl")  # Отключение опции ?отпечатка браузера?
    options.add_argument(
        f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/107.0.0.0 YaBrowser/24.7.0.0 Safari/537.36")  # Вставка гарантированного ЮзерАгента
    driver = WebDriverManagerEdge(PATH_DRIVER_EDGE, options)
    driver.get_driver()

    # Инициализация CookieManager
    cookie_manager = CookieManager(cookie_file_path)
    # Запуск драйвера
    driver.initial_driver('https://example.com')
    #Выгрузка куков
    cookie_manager.save_cookies(driver)
    # Загрузка куков
    cookie_manager.load_cookies(driver)
    #Закрытие драйвера
    driver.driver.close()
    driver.driver.quit()