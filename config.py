import json
from pathlib import path

config_path = Path(__file__).parent / "config.json"


def load_config():
	if not config_path.exists():
		raise FileNotFoundError("Config not found, please run setup.py!")
	with open(config_path) as f:
		return json.load(f)

CONFIG = load_config()
