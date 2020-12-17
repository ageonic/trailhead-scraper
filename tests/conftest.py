import pytest
from trailhead_scraper import fetch_user_id, fetch_rank_data


@pytest.fixture
def username():
    return "ecastelli"


@pytest.fixture
def incorrect_username():
    return "incorrect-username"


@pytest.fixture
def user_id(username):
    return fetch_user_id(username)


@pytest.fixture
def incorrect_user_id():
    return "incorrect-user-id"


@pytest.fixture
def earned_badge_total(username, user_id):
    return fetch_rank_data(username, user_id=user_id)["EarnedBadgeTotal"]
