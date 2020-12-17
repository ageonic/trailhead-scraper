import pytest
from trailhead_scraper import (
    fetch_user_id,
    fetch_profile_data,
    fetch_rank_data,
    fetch_awards,
)


def test_fetch_user_id(username):
    assert len(fetch_user_id(username)) == 18


def test_fetch_user_id_incorrect_username(incorrect_username):
    with pytest.raises(Exception):
        fetch_user_id(incorrect_username)


def test_fetch_profile_data(username):
    profile_data = fetch_profile_data(username)
    assert "profileUser" in profile_data

    assert profile_data["profileUser"]["LastName"] == "Castelli"
    assert profile_data["profileUser"]["FirstName"] == "Emily"


def test_fetch_profile_data_incorrect_username(incorrect_username):
    with pytest.raises(Exception):
        fetch_profile_data(incorrect_username)


def test_fetch_rank_data(username):
    rank_data = fetch_rank_data(username)
    assert "EarnedBadgeTotal" in rank_data
    assert rank_data["EarnedBadgeTotal"] > 0


def test_fetch_rank_data_incorrect_username(incorrect_username):
    with pytest.raises(Exception):
        fetch_rank_data(incorrect_username)


def test_fetch_rank_data_with_user_id(username, user_id):
    rank_data = fetch_rank_data(username, user_id=user_id)
    assert "EarnedBadgeTotal" in rank_data
    assert rank_data["EarnedBadgeTotal"] > 0


def test_fetch_rank_data_incorrect_user_id(username, incorrect_user_id):
    with pytest.raises(Exception):
        fetch_rank_data(username, user_id=incorrect_user_id)


def test_fetch_awards(username, earned_badge_total):
    awards = fetch_awards(username)
    assert len(awards) == earned_badge_total


def test_fetch_awards_incorrect_username(incorrect_username):
    with pytest.raises(Exception):
        fetch_awards(incorrect_username)


def test_fetch_awards_with_user_id(username, user_id, earned_badge_total):
    awards = fetch_awards(username, user_id=user_id)
    assert len(awards) == earned_badge_total


def test_fetch_awards_incorrect_user_id(username, incorrect_user_id):
    with pytest.raises(Exception):
        fetch_awards(username, user_id=incorrect_user_id)


def test_fetch_awards_with_total_total_badge_count(
    username, user_id, earned_badge_total
):
    awards = fetch_awards(username, limit=earned_badge_total)
    assert len(awards) == earned_badge_total


def test_fetch_awards_with_limit(username, user_id, earned_badge_total):
    lim = earned_badge_total - (earned_badge_total % 30)
    awards = fetch_awards(username, limit=lim)
    assert len(awards) == lim


def test_fetch_awards_with_user_id_and_badge_count(
    username, user_id, earned_badge_total
):
    awards = fetch_awards(username, user_id=user_id, limit=earned_badge_total)
    assert len(awards) == earned_badge_total
