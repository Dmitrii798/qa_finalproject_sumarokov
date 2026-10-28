from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class ShoppingListPage(BasePage):
    ENTRIES = (By.CSS_SELECTOR, "[class*='shopping-entry'], [class*='shoppinglist']")

    def open(self):
        return super().open("/shopping")

    def count_entries(self):
        return len(self.driver.find_elements(*self.ENTRIES))

    def has_item(self, text):
        return text.lower() in self.driver.page_source.lower()
   