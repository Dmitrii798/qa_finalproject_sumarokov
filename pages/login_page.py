from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = (By.NAME, "login")
    PASSWORD = (By.NAME, "password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    def open_login(self):
        return super().open("/accounts/login/")

    def login(self, username, password):
        self.open_login()
        self.wait.until(EC.presence_of_element_located(self.USERNAME))
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)
        self.wait.until(lambda d: "/accounts/login" not in d.current_url)
        return self
   