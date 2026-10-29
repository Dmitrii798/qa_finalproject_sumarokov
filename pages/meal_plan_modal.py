import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage


class MealPlanModal(BasePage):
    MODAL = (By.CSS_SELECTOR, ".v-overlay--active .v-card")
    FORM = (By.CSS_SELECTOR, ".v-overlay--active form.v-form")

    RECIPE_INPUT = (By.CSS_SELECTOR, "input.multiselect-search")
    MEAL_TYPE_INPUT = (By.CSS_SELECTOR, "input.multiselect-search")
    SHOPPING_CHECKBOX = (By.XPATH,
                         "//input[@aria-label='Add to Shopping List' or @aria-label='Добавить в лист покупок']")
    SAVE_BTN = (By.CSS_SELECTOR, "button.text-save")

    def _input_by_label(self, label_text: str):
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".v-overlay--active form.v-form")
        ))
        time.sleep(0.5)

        if "Заголовок" in label_text or "Title" in label_text:
            return self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 ".v-overlay--active form.v-form input[type='text']:not([aria-placeholder]):not([readonly])")
            ))
        if "Порции" in label_text or "Servings" in label_text:
            return self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 ".v-overlay--active form.v-form input[inputmode='decimal']")
            ))
        raise ValueError(f"Неизвестный label: {label_text}")

    def _type_into(self, element, text):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        ActionChains(self.driver) \
            .move_to_element(element).click(element) \
            .key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL) \
            .send_keys(Keys.DELETE) \
            .send_keys(text) \
            .send_keys(Keys.TAB) \
            .perform()
        time.sleep(0.3)

    def _select_multiselect(self, input_locator, option_text, timeout=15, index=0):
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".v-overlay--active form.v-form input.multiselect-search")
        ))
        all_inputs = self.driver.find_elements(*input_locator)
        if len(all_inputs) <= index:
            raise RuntimeError(f"Мультиселектов найдено: {len(all_inputs)}, нужен индекс {index}")
        input_el = all_inputs[index]

        input_el.click()
        time.sleep(0.3)
        input_el.clear()
        input_el.send_keys(option_text)
        print(f"DEBUG: ввели '{option_text}' в мультиселект #{index}")

        try:
            option = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     f"//li[contains(@class,'multiselect-option') "
                     f"and (contains(@aria-label, '{option_text}') "
                     f"or contains(., '{option_text}'))]")
                )
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", option
            )
            self.driver.execute_script("arguments[0].click();", option)
            print(f"DEBUG: опция '{option_text}' выбрана")
            time.sleep(0.5)
        except Exception as e:
            print(f"DEBUG: опция '{option_text}' не найдена: {e}")
            try:
                input_el.send_keys(Keys.ESCAPE)
            except Exception:
                pass

    def _set_servings(self, value):
        el = self._input_by_label("Порции")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        ActionChains(self.driver) \
            .move_to_element(el).click(el) \
            .key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL) \
            .send_keys(Keys.DELETE) \
            .send_keys(str(value)) \
            .send_keys(Keys.TAB) \
            .perform()
        time.sleep(0.3)

    def wait_modal(self):
        self.wait.until(EC.visibility_of_element_located(self.MODAL))
        self.wait.until(EC.presence_of_element_located(self.FORM))
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".v-overlay--active form.v-form input")
        ))
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".v-overlay--active form.v-form input.multiselect-search")
        ))
        time.sleep(0.5)

    def fill(self, title, recipe_name, meal_type_name="Breakfast", servings=2, add_shopping=False):
        self.wait_modal()

        self._type_into(self._input_by_label("Заголовок"), title)
        self._select_multiselect(self.RECIPE_INPUT, recipe_name, index=0)
        self._select_multiselect(self.MEAL_TYPE_INPUT, meal_type_name, index=1)
        self._set_servings(servings)
        print(f"DEBUG: порции выставлены в {servings}")

        if add_shopping:
            try:
                self.click(self.SHOPPING_CHECKBOX)
                print("DEBUG: чекбокс включён")
            except Exception:
                print("DEBUG: чекбокс не найден")

    def save(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.SAVE_BTN))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        self.driver.execute_script("arguments[0].click();", btn)
        print("DEBUG: нажата кнопка 'Создать'")
       