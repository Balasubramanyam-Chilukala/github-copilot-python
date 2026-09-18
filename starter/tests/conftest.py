import pytest

import app as app_module


@pytest.fixture(autouse=True)
def reset_game_state():
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None
    yield
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None


@pytest.fixture
def app():
    app_module.app.config.update(TESTING=True)
    yield app_module.app


@pytest.fixture
def client(app):
    return app.test_client()
