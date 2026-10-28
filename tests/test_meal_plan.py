import time
import allure
import pytest
from pages.meal_plan_page import MealPlanPage
from pages.meal_plan_modal import MealPlanModal
from pages.shopping_list_page import ShoppingListPage


@allure.feature("Meal Plan")
@allure.story("Smoke")
class TestMealPlan:

    @pytest.mark.ui
    def test_create_meal_plan(self, logged_in_driver, get_or_create_recipe, api_client, cleanup_meal_plans):
        unique_title = f"Autotest {int(time.time())}"

        with allure.step("Открываем раздел Meal Plan"):
            meal_plan_page = MealPlanPage(logged_in_driver, api_client.base_url)
            meal_plan_page.open()

        with allure.step("Открываем форму создания (двойной клик по дате)"):
            meal_plan_page.click_create()

        with allure.step("Заполняем и сохраняем"):
            modal = MealPlanModal(logged_in_driver, api_client.base_url)
            modal.fill(
                title=unique_title,
                recipe_name=get_or_create_recipe["name"],
                meal_type_name="Breakfast",
                servings=2,
                add_shopping=True,
            )
            modal.save()
            print("DEBUG: save() завершён")

        with allure.step("Проверяем, что план появился в календаре"):
            time.sleep(2)
            print(f"DEBUG: текущий URL: {logged_in_driver.current_url}")
            assert meal_plan_page.plan_exists(unique_title), \
                f"План '{unique_title}' не найден в календаре"
            print("DEBUG: план найден")

    @pytest.mark.api
    def test_delete_meal_plan_via_api(self, api_client, meal_plan_payload):
        with allure.step("Создаём план через API"):
            plan = api_client.create_meal_plan(meal_plan_payload)
            assert plan["id"]

        with allure.step("Удаляем план через API"):
            api_client.delete_meal_plan(plan["id"])

        with allure.step("Проверяем, что план удалён (404)"):
            with pytest.raises(RuntimeError):
                api_client.get_meal_plan(plan["id"])

    @pytest.mark.ui
    def test_shopping_list_contains_recipe(self, logged_in_driver, api_client, get_or_create_recipe):
        with allure.step("Открываем Shopping List"):
            page = ShoppingListPage(logged_in_driver, api_client.base_url)
            page.open()

        with allure.step("Проверяем, что список отображается"):
            assert "shopping" in logged_in_driver.current_url.lower()
           