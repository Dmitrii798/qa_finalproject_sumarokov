import os
import requests
from dotenv import load_dotenv

load_dotenv()


class TandoorAPIClient:
    def __init__(self, base_url=None, token=None):
        self.base_url = (base_url or os.getenv("BASE_URL")).rstrip("/")
        self.token = token or os.getenv("TANDOOR_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(
                f"HTTP error {e.response.status_code} on {method} {url}: "
                f"{e.response.text[:500]}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed on {method} {url}: {e}") from e

    # ---------- Recipes ----------
    def import_recipe_from_url(self, url):
        return self._make_request(
            "POST", "/api/recipe-from-source/", json={"url": url}
        )

    def get_recipes(self):
        return self._make_request("GET", "/api/recipe/")

    def get_recipe(self, recipe_id):
        return self._make_request("GET", f"/api/recipe/{recipe_id}/")

    def delete_recipe(self, recipe_id):
        return self._make_request("DELETE", f"/api/recipe/{recipe_id}/")

    def create_recipe(self, payload):
        return self._make_request("POST", "/api/recipe/", json=payload)

    # ---------- Meal Plans ----------
    def create_meal_plan(self, payload):
        return self._make_request("POST", "/api/meal-plan/", json=payload)

    def get_meal_plan(self, plan_id):
        return self._make_request("GET", f"/api/meal-plan/{plan_id}/")

    def delete_meal_plan(self, plan_id):
        return self._make_request("DELETE", f"/api/meal-plan/{plan_id}/")

    # ---------- Shopping ----------
    def get_shopping_list_entries(self, params=None):
        return self._make_request(
            "GET", "/api/shopping-list-entry/", params=params or {}
        )

    # ---------- Utils ----------
    def test_connection(self):
        data = self.get_recipes()
        print(f"✅ Connected. Recipes in account: {data.get('count')}")
        return data


if __name__ == "__main__":
    TandoorAPIClient().test_connection()
   