import os
import json

planhat_mock_api_path = os.path.abspath("utils/planhat_mock.json")
# planhat_mock_api_path = "planhat_mock.json"
# os.chdir(os.path.dirname(planhat_mock_api_path))


def load_json():
    with open(planhat_mock_api_path, "r") as f:
        response = json.load(f)
        return response


print(load_json())
