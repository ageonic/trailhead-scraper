import pytest
from trailhead_scraper import fetch_tbid, fetch_rank_data


@pytest.fixture
def username():
    return "ecastelli"


@pytest.fixture
def incorrect_username():
    return "incorrect-username"


@pytest.fixture
def tbid(username):
    return fetch_tbid(username)


@pytest.fixture
def incorrect_tbid():
    return "incorrect-tbid"


@pytest.fixture
def earned_badge_total(username, tbid):
    return fetch_rank_data(username, tbid=tbid)["EarnedBadgeTotal"]
