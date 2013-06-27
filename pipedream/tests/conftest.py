import pytest
from pipedream import Dispatcher


@pytest.fixture
def dispatcher():
    return Dispatcher()
