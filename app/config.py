import json
import os
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = os.getenv("CONFIG_PATH", "config.json")

def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Файл конфигурации {CONFIG_PATH} не найден!")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    persona_path = data.get("path_to_persona_prompt_txt")
    if persona_path and os.path.exists(persona_path):
        with open(persona_path, "r", encoding="utf-8") as pf:
            data["persona_prompt"] = pf.read().strip()
    else:
        data["persona_prompt"] = ""

    return data

config = load_config()