"""Configuration loader for .firewall.toml files."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from .models import FirewallConfig

DEFAULT_CONFIG_FILENAME = ".firewall.toml"


def find_config_file(start_dir: Path | None = None) -> Path | None:
    """Walk up directory tree to find .firewall.toml config file."""
    current = start_dir or Path.cwd()
    for parent in [current, *current.parents]:
        config_path = parent / DEFAULT_CONFIG_FILENAME
        if config_path.exists():
            return config_path
    return None


def load_config(config_path: Path | None = None) -> FirewallConfig:
    """Load config from .firewall.toml or return defaults."""
    if config_path is None:
        config_path = find_config_file()

    if config_path is None or not config_path.exists():
        config = FirewallConfig()
    else:
        with open(config_path, "rb") as f:
            raw = tomllib.load(f)
        config = FirewallConfig(**raw.get("firewall", raw))

    # Check for CI environment variables
    if os.getenv("FIREWALL_CI") == "1" or os.getenv("CI", "").lower() == "true":
        config.ci_mode = True

    return config
