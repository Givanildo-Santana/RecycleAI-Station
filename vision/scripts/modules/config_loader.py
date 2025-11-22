import os
import yaml

def load_config(base_dir):
    config_path = os.path.join(base_dir, "config.yaml")

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    return cfg
