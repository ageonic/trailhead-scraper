import requests
import re
import json

__version__ = "0.1.0"


class AuraPayload:
    """Represents a request payload for Aura Services"""

    def __init__(self, uri, action_descriptor=None):
        """Initialize the payload.

        Args:
            uri (str): The path to the Trailblazer profile page.
            action_descriptor (str, optional): The value that will be used as the descriptor value in the payload. Defaults to 'aura://ApexActionController/ACTION$execute'.
        """
        self.message = {"actions": []}
        self.aura_context = {"fwuid": "dDIdorNC3N22LalQ5i3slQ", "app": "c:ProfileApp"}
        self.aura_page_uri = uri
        self.aura_token = "undefined"
        self.action_descriptor = (
            action_descriptor or "aura://ApexActionController/ACTION$execute"
        )

    def add_action(self, class_name, method_name, inner_params):
        """Add a new Aura action to the payload.

        Args:
            class_name (str): The name of the class that contains the relevant method.
            method_name (str): The name of the method that performs the action.
            inner_params (dict): A dictionary of parameters that will be used within the params attribute. Must include a userId.
        """
        self.message["actions"].append(
            {
                "descriptor": self.action_descriptor,
                "params": {
                    "namespace": "",
                    "classname": class_name,
                    "method": method_name,
                    "params": inner_params,
                    "cacheable": False,
                    "isContinuation": False,
                },
            }
        )

    def json(self):
        """Return the payload in an appropriate format.

        Returns:
            dict: A dictionary with jsonified data.
        """
        return {
            "message": json.dumps(self.message),
            "aura.context": json.dumps(self.aura_context),
            "aura.pageURI": self.aura_page_uri,
            "aura.token": self.aura_token,
        }


class Profile:
    """A collection of user details, rank data, and awards collected from a Trailblazer profile."""

    base_url = "https://trailblazer.me"
    aura_url = base_url + "/aura"

    def __init__(self, username, tbid=None):
        """Initialize the Trailblazer profile.

        Args:
            username (str): The Trailblazer username.
            tbid (str, optional): The Trailblazer ID for the user (if available). Defaults to None.
        """
        self.username = username
        self.path = "/id/" + username
        self.url = self.base_url + self.path
        self.tbid = tbid
        self.first_name = None
        self.last_name = None

        self.rank_data = None
        self.awards = []

        # if the Trailblazer ID is not provided, retrieve it from the profile page
        if tbid is None:
            self._scrape_basics()

    def _scrape_basics(self):
        """Retrieve the Trailblazer ID, First Name, and Last Name for the current user by scraping the profile page."""
        page = requests.get(self.url)

        self.tbid = re.search(r"User\/(.*?)\\", page.text).group(1)
        self.first_name = re.search(r'FirstName\\":\\"(.*?)\\', page.text).group(1)
        self.last_name = re.search(r'LastName\\":\\"(.*?)\\', page.text).group(1)

    def _get_aura_response_body(self, payload):
        """Perform the Aura Service POST request and return the parsed response body.

        Args:
            payload (AuraPayload): The payload that will be sent with the POST request.

        Returns:
            dict: The parsed response body.
        """
        response = requests.post(self.aura_url, data=payload)

        j = json.loads(response.text)
        return json.loads(j["actions"][0]["returnValue"]["returnValue"]["body"])

    def fetch_rank_data(self):
        """Retrieve rank information for the Trailblazer user profile."""
        payload = AuraPayload(self.path)
        payload.add_action(
            "TrailheadProfileService",
            "fetchTrailheadData",
            {
                "userId": self.tbid,
            },
        )

        body = self._get_aura_response_body(payload.json())

        self.rank_data = body["value"][0]["ProfileCounts"][0]

    def fetch_awards(self):
        """Retrieve all awards for the Trailblazer user profile."""
        if self.rank_data is None:
            self.fetch_rank_data()

        for skip in range(0, self.rank_data["EarnedBadgeTotal"], 30):

            payload = AuraPayload(self.path)
            payload.add_action(
                "TrailheadProfileService",
                "fetchTrailheadBadges",
                {"userId": self.tbid, "skip": skip, "perPage": 30, "filter": "All"},
            )

            body = self._get_aura_response_body(payload.json())

            self.awards = [*self.awards, *body["value"][0]["EarnedAwards"]]
