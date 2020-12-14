import requests
import re
import json

__version__ = "0.1.0"


class AuraPayload:
    def __init__(self, uri, action_descriptor=None):
        self.message = {"actions": []}
        self.aura_context = {"fwuid": "dDIdorNC3N22LalQ5i3slQ", "app": "c:ProfileApp"}
        self.aura_page_uri = uri
        self.aura_token = "undefined"
        self.action_descriptor = (
            action_descriptor or "aura://ApexActionController/ACTION$execute"
        )

    def add_action(self, class_name, method_name, inner_params):
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
        return {
            "message": json.dumps(self.message),
            "aura.context": json.dumps(self.aura_context),
            "aura.pageURI": self.aura_page_uri,
            "aura.token": self.aura_token,
        }


class Profile:
    base_url = "https://trailblazer.me"
    aura_url = base_url + "/aura"

    def __init__(self, username, tbid=None):
        self.username = username
        self.path = "/id/" + username
        self.url = self.base_url + self.path
        self.tbid = tbid
        self.first_name = None
        self.last_name = None

        self.rank_data = None

        if tbid is None:
            self._scrape_basics()

    def _scrape_basics(self):
        """Retrieve the Trailblazer ID, First Name, and Last Name for the current user by scraping the profile page."""
        page = requests.get(self.url)

        self.tbid = re.search(r"User\/(.*?)\\", page.text).group(1)
        self.first_name = re.search(r'FirstName\\":\\"(.*?)\\', page.text).group(1)
        self.last_name = re.search(r'LastName\\":\\"(.*?)\\', page.text).group(1)

    def fetch_rank_data(self):
        payload = AuraPayload(self.path)
        payload.add_action(
            "TrailheadProfileService",
            "fetchTrailheadData",
            {
                "userId": self.tbid,
            },
        )

        response = requests.post(self.aura_url, data=payload.json())

        j = json.loads(response.text)
        body = json.loads(j["actions"][0]["returnValue"]["returnValue"]["body"])

        self.rank_data = body["value"][0]["ProfileCounts"][0]
