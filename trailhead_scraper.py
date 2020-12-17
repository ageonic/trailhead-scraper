import requests
import re
import json

__version__ = "0.1.0"

base_profile_url = "https://trailblazer.me"
aura_service_url = "https://trailblazer.me/aura"


class _AuraPayload:
    """Represents a request payload for Aura Services"""

    def __init__(self, action_descriptor=None):
        """Initialize the payload.

        Args:
            uri (str): The path to the Trailhead profile page.
            action_descriptor (str, optional): The value that will be used as the descriptor value in the payload. Defaults to 'aura://ApexActionController/ACTION$execute'.
        """
        self.message = {"actions": []}
        self.aura_context = {"fwuid": "dDIdorNC3N22LalQ5i3slQ", "app": "c:ProfileApp"}
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
            "aura.token": self.aura_token,
        }


def _build_profile_url(username):
    return "{}/id/{}".format(base_profile_url, username)


def _get_aura_response_body(payload):
    """Perform the Aura Service POST request and return the parsed response body.

    Args:
        payload (_AuraPayload): The data that will be sent with the POST request.

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


def fetch_tbid(username):
    """Retrieve the Trailblazer ID for the user by scraping the profile page."""
    page = requests.get(_build_profile_url(username))

    try:
        return re.search(r"User\/(.*?)\\", page.text).group(1)
    except:
        raise Exception(
            "Unable to retrieve TBID. The provided username may be incorrect or the profile may be private."
        )


def fetch_profile_data(username, keep_picklists=False):
    """Retrieve all profile data for the Trailhead user.

    Args:
        keep_picklists (bool, optional): Keep the 'pickLists' attribute in the profile data (JSON) retrieved from the page. Defaults to False.
    """
    page = requests.get(_build_profile_url(username))

    try:
        profile_data = json.loads(
            re.search(r'profileData = JSON.parse\("(.*?)"\)', page.text)
            .group(1)
            .replace("\\", "")
        )

        if not keep_picklists and "pickLists" in profile_data:
            del profile_data["pickLists"]

        return profile_data
    except:
        raise Exception(
            "Unable to retrieve profile data. The provided username may be incorrect."
        )


def fetch_rank_data(username, tbid=None):
    """Retrieve rank information for the Trailhead user profile."""
    payload = _AuraPayload()
    payload.add_action(
        "TrailheadProfileService",
        "fetchTrailheadData",
        {
            "userId": tbid or fetch_tbid(username),
        },
    )

    body = _get_aura_response_body(payload.data)

    return body["value"][0]["ProfileCounts"][0]


def fetch_awards(username, tbid=None, limit=None):
    """Retrieve all awards for the Trailhead user profile."""
    if tbid is None:
        tbid = fetch_tbid(username)

    if limit is None:
        limit = fetch_rank_data(username, tbid)["EarnedBadgeTotal"]

    awards = []

    for skip in range(0, limit, 30):

        payload = _AuraPayload()
        payload.add_action(
            "TrailheadProfileService",
            "fetchTrailheadBadges",
            {"userId": tbid, "skip": skip, "perPage": 30, "filter": "All"},
        )

        body = _get_aura_response_body(payload.data)

        awards = [*awards, *body["value"][0]["EarnedAwards"]]

    return awards
