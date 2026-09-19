from pathlib import Path
import yaml

PROJECT_ROOT=Path(__file__).resolve().parents[2]
CONFIG_PATH=PROJECT_ROOT/"config"/"config.yaml"

def load_config()->dict:
    with CONFIG_PATH.open("r",encoding="utf-8") as file:
        return yaml.safe_load(file)
    
