import allure
import pytest


@allure.feature("API")
@allure.story("Recipes")
class TestRecipesAPI:

    @pytest.mark.api
    def test_get_recipes_returns_results(self, api_client):
        with allure.step("GET /api/recipe/"):
            data = api_client.get_recipes()
        with allure.step("Проверяем поле results"):
            assert "results" in data
            assert isinstance(data["results"], list)

    @pytest.mark.api
    def test_create_and_delete_recipe(self, api_client):
        payload = {
            "name": "API temp recipe",
            "steps": [{"instruction": "test", "ingredients": []}],
        }
        with allure.step("Создание рецепта"):
            recipe = api_client.create_recipe(payload)
            recipe_id = recipe["id"]
        with allure.step("Проверка, что рецепт существует"):
            fetched = api_client.get_recipe(recipe_id)
            assert fetched["id"] == recipe_id
        with allure.step("Удаление рецепта"):
            api_client.delete_recipe(recipe_id)
        with allure.step("Проверка, что рецепт удалён"):
            data = api_client.get_recipes()
            ids = [r["id"] for r in data["results"]]
            assert recipe_id not in ids

    @pytest.mark.api
    def test_connection(self, api_client):
        data = api_client.test_connection()
        assert data is not None
       