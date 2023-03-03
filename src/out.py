import click
import logging
from .const import console, CACHE_DIR

__all__ = ["debug", "info", "warn", "error"]
logging.basicConfig(
    filename=CACHE_DIR / "nayur.log",
    filemode="a"
)


def debug(msg: str):
    """Prints a debug message if debugging is enabled"""
    if click.get_current_context().obj["DEBUG"]:
        console.print(f"[bold blue]{msg}")


def info(msg: str):
    """Prints an informational message"""
    console.print(f"[bold green]{msg}")


def warn(msg: str):
    """Prints a warning message"""
    console.print(f"[bold yellow]{msg}")


def error(msg: str):
    """Prints an error message"""
    console.print(f"[bold red]{msg}")
