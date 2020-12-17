import requests
import re
import json

__version__ = "0.1.0"

base_profile_url = "https://trailblazer.me"
aura_service_url = "https://trailblazer.me/aura"

aura_ctx_fwuid = "dDIdorNC3N22LalQ5i3slQ"


class _AuraPayload:
    """Represents a request payload for Aura Services"""

    def __init__(self, action_descriptor=None):
        """Initialize the payload.

        Args:
            action_descriptor (str, optional): The value that will be used as the descriptor value in the payload. Defaults to 'aura://ApexActionController/ACTION$execute'.
        """
        self.message = {"actions": []}
        self.aura_context = {"fwuid": aura_ctx_fwuid, "app": "c:ProfileApp"}
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
    """Generate a profile URL using the base profile URL and the specified username.

    Args:
        username (str): The Trailhead username for the user.

    Returns:
        str: The complete profile URL for the user.
    """
    return "{}/id/{}".format(base_profile_url, username)


def _aura_response_body(payload):
    """Perform the Aura Service POST request and yield the parsed response body for each action.

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

        yield json.loads(j["actions"][0]["returnValue"]["returnValue"]["body"])


def fetch_user_id(username):
    """Retrieve the User ID for a user by scraping the Trailhead profile page.

    Args:
        username (str): The Trailhead username for the user.

    Raises:
        Exception: Unable to retrieve User ID if the username is incorrect or the Trailhead profile is private.

    Returns:
        str: The User ID for the specified username.
    """
    page = requests.get(_build_profile_url(username))

    try:
        return re.search(r"User\/(.*?)\\", page.text).group(1)
    except:
        raise Exception(
            "Unable to retrieve user ID. The provided username may be incorrect or the profile may be private."
        )


def fetch_profile_data(username, keep_picklists=False):
    """Retrieve all profile data for the specified Trailhead username.

    Args:
        username (str): The Trailhead username for the user.
        keep_picklists (bool, optional): Keep the 'pickLists' attribute in the profile data (JSON) retrieved from the page. Defaults to False.

    Raises:
        Exception: Unable to retrieve profile data if username is incorrect.

    Returns:
        dict: The profile data retrieved from the profile page.
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


def fetch_rank_data(username, user_id=None):
    """Retrieve rank information for the specified Trailhead username.

    Args:
        username (str): The Trailhead username for the user.
        user_id (str, optional): The ID for the user. Provide this to prevent an unnecessary HTTP request. Defaults to None.

    Returns:
        dict: All rank details for the user.
    """
    payload = _AuraPayload()
    payload.add_action(
        "TrailheadProfileService",
        "fetchTrailheadData",
        {
            "userId": user_id or fetch_user_id(username),
        },
    )

    # _aura_response_body will only yield one item in this case
    # since only one action was added to the payload
    for body in _aura_response_body(payload.data):
        return body["value"][0]["ProfileCounts"][0]


def fetch_awards(username, user_id=None, limit=None):
    """Retrieve award information for the specified Trailhead username.

    Args:
        username (str): The Trailhead username for the user.
        user_id (str, optional): The ID for the user. Provide this to prevent an unnecessary HTTP request. Defaults to None.
        limit (int, optional): The maximum number of awards to return. Defaults to None and returns all awards.

    Returns:
        list: A list of awards retrieved for the user.
    """
    if user_id is None:
        user_id = fetch_user_id(username)

    if limit is None:
        limit = fetch_rank_data(username, user_id)["EarnedBadgeTotal"]

    awards = []

    for skip in range(0, limit, 30):
        payload = _AuraPayload()
        payload.add_action(
            "TrailheadProfileService",
            "fetchTrailheadBadges",
            {
                "userId": user_id,
                "skip": skip,
                "perPage": min(limit - skip, 30),
                "filter": "All",
            },
        )

        # _aura_response_body will only yield one item in this case
        # since only one action was added to the payload
        for body in _aura_response_body(payload.data):

            # end the loop if no awards are returned
            if len(body["value"][0]["EarnedAwards"]) == 0:
                return awards

            awards = [*awards, *body["value"][0]["EarnedAwards"]]

    return awards
