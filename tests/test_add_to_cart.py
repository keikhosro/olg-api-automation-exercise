import pytest
import requests
from jsonschema import validate

ADD_TO_CART_SUCCESS_SCHEMA = {
    "type": "object",
    "required": [
        "cart_id",
        "item",
        "cart_total",
        "currency",
        "created_at",
    ],
    "properties": {
        "cart_id": {"type": "string"},
        "item": {
            "type": "object",
            "required": [
                "product_id",
                "product_name",
                "quantity",
                "unit_price",
                "line_total",
            ],
            "properties": {
                "product_id": {"type": "string"},
                "product_name": {"type": "string"},
                "quantity": {"type": "integer", "minimum": 1},
                "unit_price": {"type": "number"},
                "line_total": {"type": "number"},
            },
        },
        "cart_total": {"type": "number"},
        "currency": {"type": "string", "enum": ["CAD"]},
        "created_at": {"type": "string", "format": "date-time"},
    },
}

ADD_TO_CART_ERROR_SCHEMA = {
    "type": "object",
    "required": ["error", "message", "field"],
    "properties": {
        "error": {"type": "string"},
        "message": {"type": "string"},
        "field": {"type": "string"},
    },
}


# Positive test
class TestAddToCartPositive:
    """Add a product to the cart and validate the response."""

    def test_status_code_is_201(
            self, base_url, auth_headers, valid_product_payload
    ):
        response = requests.post(
            f"{base_url}/api/cart/items",
            json=valid_product_payload,
            headers=auth_headers,
        )
        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}"
        )

    def test_response_matches_json_schema(
            self, base_url, auth_headers, valid_product_payload
    ):
        response = requests.post(
            f"{base_url}/api/cart/items",
            json=valid_product_payload,
            headers=auth_headers,
        )
        body = response.json()
        validate(instance=body, schema=ADD_TO_CART_SUCCESS_SCHEMA)

    def test_returned_product_id_matches_request(
            self, base_url, auth_headers, valid_product_payload
    ):
        response = requests.post(
            f"{base_url}/api/cart/items",
            json=valid_product_payload,
            headers=auth_headers,
        )
        body = response.json()
        assert body["item"]["product_id"] == valid_product_payload["product_id"]

    def test_quantity_matches_request(
            self, base_url, auth_headers, valid_product_payload
    ):
        response = requests.post(
            f"{base_url}/api/cart/items",
            json=valid_product_payload,
            headers=auth_headers,
        )
        body = response.json()
        assert body["item"]["quantity"] == valid_product_payload["quantity"]

    def test_line_total_equals_unit_price_times_quantity(
            self, base_url, auth_headers, valid_product_payload
    ):
        """Business logic: line_total must equal unit_price * quantity."""
        response = requests.post(
            f"{base_url}/api/cart/items",
            json=valid_product_payload,
            headers=auth_headers,
        )
        item = response.json()["item"]
        expected_total = round(item["unit_price"] * item["quantity"], 2)
        assert item["line_total"] == expected_total, (
            f"line_total {item['line_total']} != "
            f"unit_price({item['unit_price']}) * quantity({item['quantity']})"
        )

    def test_cart_total_equals_line_total(
            self, base_url, auth_headers, valid_product_payload
    ):
        """Business logic: for a single-item cart, cart_total == line_total."""
        response = requests.post(
            f"{base_url}/api/cart/items",
            json=valid_product_payload,
            headers=auth_headers,
        )
        body = response.json()
        assert body["cart_total"] == body["item"]["line_total"]

    def test_currency_is_cad(
            self, base_url, auth_headers, valid_product_payload
    ):
        response = requests.post(
            f"{base_url}/api/cart/items",
            json=valid_product_payload,
            headers=auth_headers,
        )
        assert response.json()["currency"] == "CAD"


# Negative test
class TestAddToCartNegative:
    """Attempt to add a product with an invalid quantity."""

    @pytest.mark.parametrize("bad_qty", [0, -1, -100])
    def test_invalid_quantity_returns_400(
            self, base_url, auth_headers, valid_product_id, bad_qty
    ):
        payload = {"product_id": valid_product_id, "quantity": bad_qty}
        response = requests.post(
            f"{base_url}/api/cart/items",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 400

    @pytest.mark.parametrize("bad_qty", [0, -1])
    def test_invalid_quantity_error_schema(
            self, base_url, auth_headers, valid_product_id, bad_qty
    ):
        payload = {"product_id": valid_product_id, "quantity": bad_qty}
        response = requests.post(
            f"{base_url}/api/cart/items",
            json=payload,
            headers=auth_headers,
        )
        body = response.json()
        validate(instance=body, schema=ADD_TO_CART_ERROR_SCHEMA)

    def test_invalid_quantity_error_code(self, base_url, auth_headers, valid_product_id):
        payload = {"product_id": valid_product_id, "quantity": -5}
        response = requests.post(
            f"{base_url}/api/cart/items",
            json=payload,
            headers=auth_headers,
        )
        body = response.json()
        assert body["error"] == "INVALID_QUANTITY"
        assert body["field"] == "quantity"
