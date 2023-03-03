from pathlib import Path


def dir_exists(path: Path) -> bool:
    """Checks if a directory exists."""
    return path.exists() and path.is_dir()


def dir_is_empty(path: Path) -> bool:
    """Checks if a directory is empty."""
    return dir_exists(path) and not any(path.iterdir())
