from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

opts = Options()
opts.add_argument("--headless=new")
d = webdriver.Chrome(options=opts)
try:
    d.get("https://tandoor.vs1.srv.eduson.tv/accounts/login/")
    d.find_element(By.NAME, "login").send_keys("Dmitrii")
    d.find_element(By.NAME, "password").send_keys("MZPeSzqVH5BVM29")
    d.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    time.sleep(3)
    d.get("https://tandoor.vs1.srv.eduson.tv/mealplan")
    time.sleep(3)
    d.find_element(By.XPATH, "//div[@aria-haspopup='dialog']").click()
    time.sleep(3)

    # Ищем всё про "Заголовок"
    labels = d.find_elements(By.XPATH, "//label[contains(normalize-space(.), 'Заголовок')]")
    print(f"Labels found: {len(labels)}")
    for l in labels:
        print(f"  class={l.get_attribute('class')} for={l.get_attribute('for')}")

    inputs1 = d.find_elements(By.XPATH, "//label[contains(normalize-space(.), 'Заголовок')]/following-sibling::input")
    print(f"Inputs (following-sibling): {len(inputs1)}")
    for i in inputs1:
        print(f"  id={i.get_attribute('id')}")

    # Все input внутри формы модалки
    inputs2 = d.find_elements(By.CSS_SELECTOR, ".v-overlay--active form.v-form input")
    print(f"All inputs in modal: {len(inputs2)}")
    for i in inputs2:
        print(
            f"  id={i.get_attribute('id')} type={i.get_attribute('type')} placeholder={i.get_attribute('placeholder')} aria-label={i.get_attribute('aria-label')}")

    # Ищем по aria-labelledby
    inputs3 = d.find_elements(By.XPATH, "//input[@aria-labelledby='input-v-0-6-label']")
    print(f"Inputs by aria-labelledby='input-v-0-6-label': {len(inputs3)}")
finally:
    d.quit()
   