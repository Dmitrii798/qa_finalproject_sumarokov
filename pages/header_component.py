from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class HeaderComponent(BasePage):
    MEAL_PLAN_LINK = (By.CSS_SELECTOR, "a[href='/mealplan']")
    SHOPPING_LINK = (By.CSS_SELECTOR, "a[href='/shopping']")
    USER_MENU = (By.CSS_SELECTOR, ".navbar .dropdown-toggle")

    def go_to_meal_plan(self):
        self.click(self.MEAL_PLAN_LINK)
        return self

    def go_to_shopping(self):
        self.click(self.SHOPPING_LINK)
        return self

    def is_authorized(self):
        try:
            self.find(self.USER_MENU)
            return True
        except Exception:
            return False
       