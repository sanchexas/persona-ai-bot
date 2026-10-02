import json
import os
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = os.getenv("CONFIG_PATH", "config.json")

config: dict = {}

def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"File {CONFIG_PATH} not found.")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    persona_path = data.get("path_to_persona_prompt_txt")
    if persona_path and os.path.exists(persona_path):
        with open(persona_path, "r", encoding="utf-8") as pf:
            data["persona_prompt"] = pf.read().strip()
    else:
        data["persona_prompt"] = ""

    config.clear()
    config.update(data)
    return config

load_config()