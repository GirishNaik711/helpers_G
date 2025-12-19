import pytest
from fastapi.testclient import TestClient

import api.main as api_main


@pytest.fixture()
def client():
    return TestClient(api_main.app)
