import json
import pathlib
import logging.config

def setup_logging():
    config_file = pathlib.Path("config/logging.json")
    with open(config_file, "r") as f:
        config = json.load(f)
    logging.config.dictConfig(config)