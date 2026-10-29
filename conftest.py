import os
import json
import time
import pytest
import allure
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

from api.client import TandoorAPIClient

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("TANDOOR_USERNAME")
PASSWORD = os.getenv("TANDOOR_PASSWORD")


# ---------- API ----------
@pytest.fixture(scope="session")
def api_client():
    return TandoorAPIClient()


@pytest.fixture(scope="session")
def get_or_create_recipe(api_client):
    """Возвращает существующий рецепт или создаёт новый через API."""
    data = api_client.get_recipes()
    if data and data.get("count", 0) > 0:
        return data["results"][0]

    payload = {
        "name": "Autotest Recipe",
        "steps": [{"instruction": "Mix and cook", "ingredients": []}],
    }
    return api_client.create_recipe(payload)


@pytest.fixture
def meal_plan_payload(get_or_create_recipe):
    """Уникальное название на каждый прогон, чтобы не было дублей."""
    now = datetime.now().replace(microsecond=0)
    unique_title = f"Autotest {now.strftime('%Y%m%d_%H%M%S')}"
    return {
        "title": unique_title,
        "recipe": get_or_create_recipe["id"],
        "servings": 2,
        "from_date": now.isoformat(),
        "to_date": (now + timedelta(hours=1)).isoformat(),
        "meal_type": 470,
        "note": "created by autotest",
    }


@pytest.fixture
def cleanup_meal_plans(api_client):
    """После теста удаляет все планы с 'Autotest' в названии."""
    yield
    try:
        plans = api_client._make_request("GET", "/api/meal-plan/?page_size=100")
        for p in plans.get("results", []):
            title = p.get("title", "")
            if "Autotest" in title:
                try:
                    api_client.delete_meal_plan(p["id"])
                    print(f"CLEANUP: удалён план id={p['id']} title={title}")
                except Exception as e:
                    print(f"CLEANUP: ошибка удаления id={p['id']}: {e}")
    except Exception as e:
        print(f"CLEANUP: ошибка — {e}")


# ---------- UI ----------
@pytest.fixture
def driver():
    opts = Options()
    if os.getenv("CI") or os.getenv("HEADLESS", "1") == "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--force-device-scale-factor=1")

    remote = os.getenv("SELENIUM_REMOTE_URL")
    if remote:
        drv = webdriver.Remote(command_executor=remote, options=opts)
    else:
        drv = webdriver.Chrome(options=opts)

    drv.implicitly_wait(5)
    yield drv
    try:
        drv.quit()
    except Exception:
        pass


@pytest.fixture
def logged_in_driver(driver):
    from pages.login_page import LoginPage
    LoginPage(driver, BASE_URL).login(USERNAME, PASSWORD)
    assert "/accounts/login" not in driver.current_url, \
        f"Логин не удался. URL: {driver.current_url}"
    return driver


# ---------- Screenshot hook ----------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if drv:
            try:
                allure.attach(
                    drv.get_screenshot_as_png(),
                    name="screenshot_on_failure",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass
          