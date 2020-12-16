import requests
import re
import json

__version__ = "0.1.0"

base_profile_url = "https://trailblazer.me"
aura_service_url = "https://trailblazer.me/aura"


class _AuraPayload:
    """Represents a request payload for Aura Services"""

    def __init__(self, uri, action_descriptor=None):
        """Initialize the payload.

        Args:
            uri (str): The path to the Trailhead profile page.
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

    @property
    def data(self):
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


def _get_tbid(url):
    """Retrieve the Trailblazer ID for the user by scraping the profile page."""
    page = requests.get(url)

    try:
        return re.search(r"User\/(.*?)\\", page.text).group(1)
    except:
        # raise an exception if the tbid is not found - this prevents any of the other methods from being executed
        raise Exception(
            "The TBID was not found for '{}'. The provided URL may be incorrect or the profile may be private.".format(
                url
            )
        )


def _get_aura_response_body(payload):
    """Perform the Aura Service POST request and return the parsed response body.

    Args:
        payload (_AuraPayload): The payload that will be sent with the POST request.

    Returns:
        dict: The parsed response body.
    """
    response = requests.post(aura_service_url, data=payload)

    j = response.json()

    for action in j["actions"]:
        if action["state"] == "ERROR":
            raise Exception(
                "Aura Action Error: {}".format(action["error"][0]["message"])
            )

    return json.loads(j["actions"][0]["returnValue"]["returnValue"]["body"])


class TrailheadProfile:
    """A collection of user details, rank data, and awards collected from a Trailhead profile."""

    def __init__(self, username, tbid=None):
        """Initialize the Trailhead profile.

        Args:
            username (str): The Trailhead username.
            tbid (str, optional): The Trailblazer ID for the user (if available). Defaults to None.
        """
        self.username = username
        self.path = "/id/" + username
        self.url = base_profile_url + self.path
        self.tbid = tbid

        self.profile_data = None
        self.rank_data = None
        self.awards = []

        # if the Trailblazer ID is not provided, retrieve it from the profile page
        if tbid is None:
            self.tbid = _get_tbid(self.url)

    def fetch_profile_data(self, keep_picklists=False):
        """Retrieve all profile data for the Trailhead user.

        Args:
            keep_picklists (bool, optional): Keep the 'pickLists' attribute in the profile data (JSON) retrieved from the page. Defaults to False.
        """
        page = requests.get(self.url)

        self.profile_data = json.loads(
            re.search(r'profileData = JSON.parse\("(.*?)"\)', page.text)
            .group(1)
            .replace("\\", "")
        )

        if not keep_picklists and "pickLists" in self.profile_data:
            del self.profile_data["pickLists"]

    def fetch_rank_data(self):
        """Retrieve rank information for the Trailhead user profile."""
        payload = _AuraPayload(self.path)
        payload.add_action(
            "TrailheadProfileService",
            "fetchTrailheadData",
            {
                "userId": self.tbid,
            },
        )

        body = _get_aura_response_body(payload.data)

        self.rank_data = body["value"][0]["ProfileCounts"][0]

    def fetch_awards(self):
        """Retrieve all awards for the Trailhead user profile."""
        if self.rank_data is None:
            self.fetch_rank_data()

        for skip in range(0, self.rank_data["EarnedBadgeTotal"], 30):

            payload = _AuraPayload(self.path)
            payload.add_action(
                "TrailheadProfileService",
                "fetchTrailheadBadges",
                {"userId": self.tbid, "skip": skip, "perPage": 30, "filter": "All"},
            )

            body = _get_aura_response_body(payload.data)

            self.awards = [*self.awards, *body["value"][0]["EarnedAwards"]]
