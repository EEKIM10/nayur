from rich import get_console
import requests
from pathlib import Path

__all__ = (
    "console",
    "session",
    "CACHE_DIR"
)

console = get_console()
session = requests.Session()
CACHE_DIR = Path.home() / ".cache" / "nayur"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
