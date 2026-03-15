import os
from dotenv import load_dotenv
import pytest

load_dotenv()

BASE_URL = os.environ["BASE_URL"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]

PRODUCT_ID = "prod_NWjs8kKbJWmuuc"


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def auth_headers():
    return {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json",
    }


@pytest.fixture
def valid_product_payload():
    return {
        "product_id": PRODUCT_ID,
        "quantity": 2,
    }


@pytest.fixture
def valid_product_id():
    return PRODUCT_ID
