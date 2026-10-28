import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, 15)

    def open(self, path=""):
        self.driver.get(f"{self.base_url}/{path.lstrip('/')}")
        return self

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text, clear=True):
        el = self.find(locator)
        if clear:
            el.clear()
        el.send_keys(text)

    def text_of(self, locator):
        return self.find(locator).text

    def debug_screenshot(self, name="debug"):
        os.makedirs("debug", exist_ok=True)
        self.driver.save_screenshot(f"debug/{name}.png")
        with open(f"debug/{name}.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        print(f"🖼  Скриншот: debug/{name}.png")
        print(f"📄 HTML: debug/{name}.html")
        print(f"🌐 Текущий URL: {self.driver.current_url}")
       