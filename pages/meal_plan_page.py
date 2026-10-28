import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage


class MealPlanPage(BasePage):
    DAY_CELLS = (By.CSS_SELECTOR, ".cv-day")
    TODAY_CELL = (By.CSS_SELECTOR, ".cv-day.today")
    MODAL_FORM = (By.CSS_SELECTOR, ".v-overlay-container form.v-form")

    @staticmethod
    def plan_locator(title):
        return (By.XPATH, f"//*[contains(normalize-space(text()), '{title}')]")

    def open(self):
        self.driver.get(f"{self.base_url}/mealplan")
        self.wait.until(EC.presence_of_element_located(self.DAY_CELLS))
        return self

    def click_create(self):
        self.wait.until(EC.presence_of_element_located(self.DAY_CELLS))

        for attempt in range(1, 4):
            # Находим ячейку заново на каждой итерации
            cell = self.driver.find_element(*self.TODAY_CELL)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cell)
            self.driver.execute_script("arguments[0].click();", cell)
            print(f"DEBUG: клик №{attempt} по ячейке дня")

            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located(self.MODAL_FORM)
                )
                print("DEBUG: модалка реально открылась (форма есть)")
                break
            except Exception:
                print(f"DEBUG: после клика №{attempt} форма не появилась")

        self.wait.until(EC.presence_of_element_located(self.MODAL_FORM))

    def plan_exists(self, title):
        try:
            self.find(self.plan_locator(title))
            return True
        except Exception:
            return False
       