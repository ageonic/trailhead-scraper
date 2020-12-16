import pytest
from trailhead_scraper import TrailheadProfile


def test_tbid_provided():
    test_tbid = "testtbid"
    u = TrailheadProfile("ecastelli", test_tbid)
    assert u.tbid == test_tbid


def test_correct_username():
    u = TrailheadProfile("ecastelli")
    assert len(u.tbid) == 18


def test_incorrect_username():
    with pytest.raises(Exception):
        TrailheadProfile("incorrect_username")


def test_fetch_profile_data():
    u = TrailheadProfile("ecastelli")
    assert u.profile_data is None
    u.fetch_profile_data()
    assert u.profile_data is not None
    assert "profileUser" in u.profile_data

    assert u.profile_data["profileUser"]["FirstName"] == "Emily"
    assert u.profile_data["profileUser"]["LastName"] == "Castelli"


def test_fetch_rank_data():
    u = TrailheadProfile("ecastelli")
    assert u.rank_data is None
    u.fetch_rank_data()
    assert u.rank_data is not None
    assert "Id" in u.rank_data


def test_fetch_awards():
    u = TrailheadProfile("ecastelli")
    assert len(u.awards) <= 0
    u.fetch_awards()
    assert len(u.awards) > 0
