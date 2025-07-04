from pathlib import Path

# This gives you the root of the project regardless of where the script is run from
PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"