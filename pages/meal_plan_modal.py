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

    RECIPE_INPUT = (By.CSS_SELECTOR, "input.multiselect-search[aria-placeholder='Рецепт']")
    MEAL_TYPE_INPUT = (By.CSS_SELECTOR, "input.multiselect-search[aria-placeholder='Тип питания']")
    SHOPPING_CHECKBOX = (By.XPATH, "//input[@aria-label='Добавить в лист покупок']")
    SAVE_BTN = (By.CSS_SELECTOR, "button.text-save")

    # ---- Хелперы ----
    def _input_by_label(self, label_text: str):
        # 1. Сначала ждём, что в модалке реально есть input'ы
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".v-overlay--active form.v-form input")
        ))
        # 2. Ищем input, у которого label (по aria-labelledby) содержит нужный текст
        # Это работает даже если label отрисован позже
        inputs = self.driver.find_elements(
            By.CSS_SELECTOR, ".v-overlay--active form.v-form input"
        )
        for inp in inputs:
            labelled_by = inp.get_attribute("aria-labelledby")
            if not labelled_by:
                continue
            try:
                label_el = self.driver.find_element(By.ID, labelled_by)
                if label_text in label_el.text:
                    return inp
            except Exception:
                continue

        # 3. Fallback — ищем по тексту label (как раньше)
        label = self.wait.until(EC.presence_of_element_located(
            (By.XPATH,
             f"//div[contains(@class,'v-overlay--active')]"
             f"//label[contains(normalize-space(.), '{label_text}') "
             f"and @aria-hidden='false']")
        ))
        label_id = label.get_attribute("id")
        if not label_id:
            raise RuntimeError(f"У label '{label_text}' нет id")
        return self.wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//input[@aria-labelledby='{label_id}']")
        ))

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

    def _select_multiselect(self, input_locator, option_text, timeout=8):
        input_el = self.find(input_locator)
        input_el.click()
        time.sleep(0.3)
        input_el.clear()
        input_el.send_keys(option_text)
        print(f"DEBUG: ввели '{option_text}' в мультиселект")

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
        """Точное значение через ввод (не через +/-)."""
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

    # ---- API ----
    def wait_modal(self):
        self.wait.until(EC.visibility_of_element_located(self.MODAL))
        self.wait.until(EC.presence_of_element_located(self.FORM))
        # ⬇️ Дожидаемся именно полей, а не только формы
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".v-overlay--active form.v-form input")
        ))
        time.sleep(0.3)

    def fill(self, title, recipe_name, meal_type_name="Breakfast", servings=2, add_shopping=False):
        self.wait_modal()

        # Заголовок
        self._type_into(self._input_by_label("Заголовок"), title)

        # Рецепт
        self._select_multiselect(self.RECIPE_INPUT, recipe_name)

        # Тип питания
        self._select_multiselect(self.MEAL_TYPE_INPUT, meal_type_name)

        # Порции
        self._set_servings(servings)
        print(f"DEBUG: порции выставлены в {servings}")

        # Чекбокс
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
     