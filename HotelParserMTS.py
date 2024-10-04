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

class HotelParserMTS:
    def __init__(self, hotel_data: dict, limit_rooms=None, path_cookies=None):
        # hotel_data = {hotels:[{hotel_db_id1: int, hotel_url1: str}, {hotel_db_idN: int, hotel_urlN: str}]}
        # hotel_url = / rossiya / moskva / cosmos_moscow_vdnh_hotel_(kosmos_vdnh)?title = Москва
        self.hotel_data = hotel_data
        self.limit_rooms = 50 if limit_rooms is None else limit_rooms # Без реализации
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

    def parse_rooms(self):
        cookie_manager = CookieManager(self.path_cookies)
        self.driver.get_driver()
        cookie_manager.save_cookies(self.driver, 'https://travel.mts.ru/hotels/')
        cookie_manager.load_cookies(self.driver)
        hotels = self.hotel_data.get('hotels', [])
        page = 1
        result = list()
        for hotel in hotels:
            for day in range(1, 10): #Мониторинг цен на 10 дней вперед
                hotel_db_id = hotel["hotelDbId"]
                hotel_url = hotel["hotelUrl"]
                print("Обработка:", hotel_db_id, " ", hotel_url)
                # Получаем завтрашнюю и послезавтрашнюю дату
                tomorrow = datetime.now() + timedelta(days=day)
                day_after_tomorrow = datetime.now() + timedelta(days=day+1)
                # Форматируем даты в нужный формат 'YYYY-MM-DD'
                tomorrow_str = tomorrow.strftime('%Y-%m-%d')
                day_after_tomorrow_str = day_after_tomorrow.strftime('%Y-%m-%d')

                # Реализован поиск только двух местных номеров
                url = f"https://travel.mts.ru/hotels{str(hotel_url)}&checkin={tomorrow_str}&checkout={day_after_tomorrow_str}&adults=2&children=0&page={page}"

                self.driver.initial_driver(url)
                time.sleep(5)

                json_data = dict()
                try:
                    for request in self.driver.driver.requests:
                        if re.match(r'.+/properties/.+/offers-search', str(request.url)):  # Проверяем, есть ли ответ на запрос
                            body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                            json_data = json.loads(body)
                            #print(json_data)
                            for room in json_data['offer']['roomsOffers']:
                                number_id = room['roomId']
                                name = room['roomName']
                                price = room['tariff']['totalPrice']['amount']['value']
                                # Создаем словарь для текущего номера и добавляем его в список
                                result.append({
                                    'hotelDbId': hotel_db_id,
                                    'numbers': [{
                                        'numberId': number_id,
                                        'name': str(name),
                                        'capasity': 2,
                                        'wifi': True,
                                        'priceStart': str(tomorrow_str),
                                        'priceEnd': str(day_after_tomorrow_str),
                                        'price': "{:.2f}".format(price / 100),
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
    hotel_data = {'hotels':[{'hotelDbId': 1, 'hotelUrl': u'/rossiya/moskva/cosmos_moscow_vdnh_hotel_(kosmos_vdnh)?title=Москва'}]}
    hotels = hotel_data.get('hotels', [])
    hotel_parser = HotelParserMTS(hotel_data)
    hotel_parser.parse_rooms()