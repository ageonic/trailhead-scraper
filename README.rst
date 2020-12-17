===================
Trailhead Scraper
===================

|license|   |tests|

.. |license| image:: https://shields.io/badge/License-MIT-blue

.. |tests| image:: https://github.com/ang3orge/trailhead-scraper/workflows/Tests/badge.svg
   :alt: Trailhead Scraper Tests status on GitHub Actions
   :target: https://github.com/ang3orge/trailhead-scraper/actions

A simple package that enables retrieval of public data from Salesforce Trailhead user profiles.

Installation
------------

trailhead-scraper can be installed via ``pip``:

.. code-block:: sh

   $ pip install trailhead-scraper

Quickstart
----------

You can now retrieve information about a Trailhead user based on a username:

.. code-block:: python

   from trailhead_scraper import fetch_profile_data, fetch_rank_data, fetch_awards

   username = "trailhead-username"

   # get profile information
   profile = fetch_profile_data(username)

   # get rank information
   rank_data = fetch_rank_data(username)

   # get list of awards (badges)
   awards = fetch_awards(username)

Use the profile data to access basic information about the user:

.. code-block:: python

   print(profile["profilePhotoUrl"])
   print(profile["profileUser"]["FirstName"])
   print(profile["profileUser"]["LastName"])
   print(profile["profileUser"]["CompanyName"])
   print(profile["profileUser"]["Title"])

Use the rank data to get the user's rank and related information:

.. code-block:: python

   print(rank_data["RankLabel"])
   print(rank_data["RankImageUrl"])
   print(rank_data["EarnedPointTotal"])
   print(rank_data["EarnedBadgeTotal"])
   print(rank_data["CompletedTrailTotal"])
   print(rank_data["PointTotalForNextRank"])
   print(rank_data["BadgeTotalForNextRank"])

The list of awards contains details about each award (badge/recognition) earned by the user:

.. code-block:: python

   for award in awards:
      print(award["AwardType"], award["Award"]["Label"])
