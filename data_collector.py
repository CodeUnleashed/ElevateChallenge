import requests
import json
from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List

# DON'T DO! It is a bad idea to save the credentials in text.
username = "elevateinterviews"
password = "ElevateSecurityInterviews2021"

PRIORITY_LEVELS = ["low", "medium", "high", "critical"]

ENDPOINTS = {
    "denial": "reported_by",
    "intrusion": "internal_ip",
    "executable": "machine_ip",
    "misuse": "employee_id",
    "unauthorized": "employee_id",
    "probing": "ip",
    "other": "identifier",
}

BASE_URL = "https://incident-api.use1stag.elevatesecurity.io"
INCIDENTS_ENDPOINT = f"{BASE_URL}/incidents/"
IDENTITIES_ENDPOINT = f"{BASE_URL}/identities/"


class DataCollector:
    _INCIDENTS_FILENAME: str = "incidents.json"
    _user_data: _Dict[str, _Dict[str, _Dict[str, int | _List[_Dict[str, _Any]]]]] = {}
    _identities: _Dict[str, int]

    def __init__(self) -> None:
        self._identities = self._retrieve_identities()

    def _insert_new_incident(
        self, incident_info: _Dict[str, str], incidents: _List[_Dict[str, _Any]]
    ) -> _List[_Dict[str, _Any]]:
        if len(incidents) == 0:
            return [incident_info]

        for index, incident in enumerate(incidents):
            if incident_info["timestamp"] > incident["timestamp"]:
                incidents[index:index] = [incident_info]
                return incidents

        return incidents + [incident_info]

    def _process_item(
        self, item: _Dict[str, _Any], user_key: str, incident_type: str
    ) -> _Dict[str, _Any]:
        # Coverting the user_id to a string because this can be an int.
        user_id = str(item[user_key])

        # Simple check to verify this is an ip address.
        if "." in user_id:
            # Coverting the identities to a string because this can be an int.
            user_id = str(self._identities[item[user_key]])

        info_dict = {"type": incident_type}
        info_dict.update(item)

        if user_id not in self._user_data:
            self._user_data[user_id] = {}
            for pl in PRIORITY_LEVELS:
                self._user_data[user_id].update({pl: {"count": 0, "incidents": []}})

        if (
            info_dict
            not in self._user_data[user_id][info_dict["priority"]]["incidents"]
        ):
            self._user_data[user_id][info_dict["priority"]]["count"] += 1
            self._user_data[user_id][info_dict["priority"]][
                "incidents"
            ] = self._insert_new_incident(
                info_dict, self._user_data[user_id][info_dict["priority"]]["incidents"]
            )

    def _retrieve_identities(self):
        response = requests.get(IDENTITIES_ENDPOINT, auth=(username, password))
        return json.loads(response.text)

    def retrieve_data_from_endpoints(self):
        for incident_type, user_key in ENDPOINTS.items():
            # We are going to give the request a 10 second timeout.
            response = requests.get(
                f"{INCIDENTS_ENDPOINT}{incident_type}",
                auth=(username, password),
                timeout=10,
            )
            response_d = json.loads(response.text)

            for item in response_d["results"]:
                self._process_item(item, user_key, incident_type)

    def save_data_to_file(self):
        with open(self._INCIDENTS_FILENAME, "w+") as f:
            f.write(json.dumps(self._user_data, sort_keys=True))
