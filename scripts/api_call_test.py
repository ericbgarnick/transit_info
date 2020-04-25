import json
from typing import Dict

import requests

BASE_URL = "https://api-v3.mbta.com/"


def get_stops() -> Dict:
    resource = "stops"
    headers = {"x-api-key": "ba5f4b53533a42c595a7eb1cc854ee7b"}
    response = requests.get(BASE_URL + resource, headers=headers)

    content = json.loads(response.content.decode('utf-8'))

    ids_for_names = {stop['attributes']['name']: stop['id'] for stop in content['data']}
    # print(json.dumps(ids_for_names, indent=4, sort_keys=True))
    return ids_for_names


def get_stop(stop_id: str) -> Dict:
    resource = "stops"
    headers = {"x-api-key": "ba5f4b53533a42c595a7eb1cc854ee7b"}
    response = requests.get(BASE_URL + resource + f'/{stop_id}', headers=headers)

    return json.loads(response.content.decode('utf-8'))


if __name__ == '__main__':
    get_stops()
