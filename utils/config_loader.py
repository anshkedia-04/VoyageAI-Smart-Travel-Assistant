from pathlib import Path
from typing import Any

import yaml

from exception.exceptionhandling import ConfigurationError

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config(config_path: str | Path = "config/config.yaml") -> dict[str, Any]:
    """Load YAML configuration relative to the project root if not absolute."""
    path = Path(config_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.exists():
        raise ConfigurationError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}
    return config
