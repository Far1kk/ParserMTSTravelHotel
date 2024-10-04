from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from config import PATH_DRIVER_EDGE

class WebDriverManagerEdge:
    def __init__(self, driver_path, options=None):
        self.options = options if options else EdgeOptions()
        self.driver_path = driver_path
        self.driver = None

    def get_driver(self):
        # Если указан путь к драйверу, используем его
        service = EdgeService(self.driver_path)
        self.driver = webdriver.Edge(service=service, options=self.options)
        return self.driver

    def initial_driver(self, url: str):
        self.driver.get(url)
