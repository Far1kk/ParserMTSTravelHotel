import json
from CookieManager import CookieManager
from WebDriverManager import WebDriverManagerEdge
from selenium.webdriver.edge.options import Options
from seleniumwire.utils import decode
from datetime import datetime, timedelta
import time
from config import PATH_DRIVER_EDGE
from config import PATH_COOKIE_MTS
import re

class RegionParserMTS:
    def __init__(self, region_data: dict, limit_hotels=None, path_cookies=None):
        # region_data = {regions:[{region_db_id1: int, region_url1: str}, {region_db_idN: int, region_urlN: str}]}
        # region_url = / rossiya / moskva / cosmos_moscow_vdnh_hotel_(kosmos_vdnh)?title = Москва
        self.region_data = region_data
        self.limit_rooms = 50 if limit_hotels is None else limit_hotels # Без реализации
        options = Options()
        options.use_chromium = True  # Использование Chromium-совместимую версию Edge
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')  # Отключение опции автоматизированного ПО
        options.add_argument("--disable-extensions")  # Отключение опции расширений
        options.add_argument("--disable-webgl")  # Отключение опции ?отпечатка браузера?
        options.add_argument(
            f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/107.0.0.0 YaBrowser/24.7.0.0 Safari/537.36") # Вставка гарантированного ЮзерАгента
        options.page_load_strategy = 'none'
        self.driver = WebDriverManagerEdge(PATH_DRIVER_EDGE, options=options)
        self.path_cookies = PATH_COOKIE_MTS if path_cookies is None else path_cookies

    def parse_hotels(self):
        cookie_manager = CookieManager(self.path_cookies)
        self.driver.get_driver()
        cookie_manager.save_cookies(self.driver, 'https://travel.mts.ru/hotels/')
        cookie_manager.load_cookies(self.driver)
        regions = self.region_data.get('regions', [])
        result = list()
        # Получаем дату через въезда 10 дней и выезда 11 дней
        tomorrow = datetime.now() + timedelta(days=10)
        day_after_tomorrow = datetime.now() + timedelta(days=11)
        # Форматируем даты в нужный формат 'YYYY-MM-DD'
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        day_after_tomorrow_str = day_after_tomorrow.strftime('%Y-%m-%d')
        for region in regions:
            for page in range(1, 10): #Мониторинг отелей на 10 страницах (обычно по 30 на одной странице)
                region_db_id = region["regionDbId"]
                region_url = region["regionUrl"]
                city = region["city"]
                print("Обработка:", region_db_id, " ", region_url)

                # Реализован поиск только двухместных номеров
                url = f"https://travel.mts.ru/search/hotels{str(region_url)}&checkin={tomorrow_str}&checkout={day_after_tomorrow_str}&adults=2&children=0&page={page}&sort=recommendation%2Cdesc&limit=30"

                self.driver.initial_driver(url)
                time.sleep(5)

                json_data = dict()
                try:
                    for request in self.driver.driver.requests:
                        if re.match(r'.+v2/offers-searchResult', str(request.url)):  # Проверяем, есть ли ответ на запрос
                            body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                            json_data = json.loads(body)
                            #print(json_data)
                            for offer in json_data['offers']:
                                property_data = offer.get("property", {})
                                address = property_data.get("address")
                                name = property_data.get("name")
                                hotel_id = property_data.get("id")
                                aliases = property_data.get("aliases")
                                urlAddress = f'/{aliases.get('countryAlias')}/{aliases.get('cityAlias')}/{aliases.get('alias')}'
                                # В property находятся другие интересные данные
                                # Создаем словарь для текущего региона и добавляем его в список
                                result.append({
                                    'regionDbId': region_db_id,
                                    'hotels': [{
                                        'hotelId': str(hotel_id),
                                        'name': str(name),
                                        'address': f'г.{city} {urlAddress}',
                                        'urlAddress': str(urlAddress),
                                        'dateParse': datetime.now().strftime('%Y-%m-%d')
                                    }]
                                })
                        else:
                            pass
                except Exception as e:
                    print('Ошибка при заборе асинхронных запросов: ', e)
                print(result)
        self.driver.driver.close()
        self.driver.driver.quit()

if __name__ == "__main__":
    region_data = {'regions':[{'regionDbId': 1, 'regionUrl': u'/rossiya/moskva?title=Москва', 'city': 'Москва'}]}
    regions = region_data.get('regions', [])
    region_parser = RegionParserMTS(region_data)
    region_parser.parse_hotels()
'''https://travel.mts.ru/hotels/rossiya/moskva/royal_zenit_ii_1?page=1
&checkin=2024-10-03&checkout=2024-10-04&location=52e439e5-107f-401f-8982-5a0645fcdc63&adults=2&children=0'''