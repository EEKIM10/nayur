import os

import click
import sys
import subprocess
import shutil
import requests
import glob
import platform
import logging
from typing import Tuple

from .const import console, CACHE_DIR, session
from .out import error, warn, info, debug as _debug
from .lib import dir_exists, dir_is_empty

logger = logging.getLogger(__name__)


@click.group()
@click.option("--debug", is_flag=True, help="Enables debug mode.")
@click.option(
    "--log-level", "-L", type=click.Choice(
        ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"), case_sensitive=False
    ),
    default="INFO",
    help="The log level to put into the ~/.cache/nayur/nayur.log file."
)
@click.pass_context
def main(ctx: click.Context, debug: bool, log_level: str):
    """Nayur - the least helpful AUR helper"""
    logger.setLevel(getattr(logging, log_level.upper()))
    getattr(logger, log_level.lower())("Log level is set to: " + log_level.lower())
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    if ctx.invoked_subcommand is None:
        error("[bold red]No subcommand specified.")
        error(f"Run [bold cyan]{sys.argv[0]} --help[/bold cyan] for help.")
        return


@main.group()
def cache():
    """Cache-related commands"""


@cache.command()
@click.argument("pkg_names", required=True, type=str, nargs=-1)
def get(pkg_names: Tuple[str]):
    """Downloads a package

    This does not install it."""
    for pkg_name in pkg_names:
        with console.status(f"[bold green]Preparing {pkg_name}") as status:
            pkg_name = pkg_name.lower()

            status.update("[bold green]Making cache directory")
            pkg_path = CACHE_DIR / pkg_name
            if pkg_path.exists():
                console.print(f"[red]Package {pkg_name} already exists in cache.")
                continue

            pkg_path.mkdir(parents=True, exist_ok=True)

            status.update(f"[bold green]Retrieving metadata for {pkg_name}")
            try:
                url = "https://aur.archlinux.org/rpc/v5/info/" + pkg_name
                logger.debug("GET " + url)
                response: requests.Response = session.get(url)
                logger.debug(
                    f"HTTP {response.status_code} {response.reason}"
                )
                logger.debug(response.text)
                _debug(f"Response ({response.status_code}): {response.json()}")
                response.raise_for_status()
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
                logger.error("Failed to download metadata", e)
                error(f"[red]Failed to download {pkg_name} metadata. {e}")
                shutil.rmtree(pkg_path)
                continue

            if response.json()["resultcount"] == 0:
                error(f"Package {pkg_name} not found.")
                continue

            status.update(f"[bold green]Cloning {pkg_name} repository")
            try:
                result = subprocess.run(
                    (
                        "git",
                        "clone",
                        f"https://aur.archlinux.org/{pkg_name}.git",
                        str(pkg_path),
                    ),
                    capture_output=True,
                    encoding="utf-8",
                )
                _debug("Exit code: " + str(result.returncode))
                _debug("STDOUT:")
                _debug(result.stdout)
                _debug("\nSTDERR:")
                _debug(result.stderr)
                result.check_returncode()
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Failed to clone repository {pkg_name}. {e}")
                shutil.rmtree(pkg_path)
                continue
            else:
                if not any(pkg_path.iterdir()):
                    warn(f"Warn - {pkg_name} (empty repository)")
                info(f"Ok - {pkg_name}")


@cache.command(name="list")
def _list():
    """Lists all packages in the cache"""
    with console.status("[bold green]Preparing") as status:
        status.update("[bold green]Listing packages")
        for pkg in sorted(CACHE_DIR.iterdir(), key=lambda p: p.name):
            if (CACHE_DIR / pkg).is_dir() is False:
                continue
            if not dir_is_empty(CACHE_DIR / pkg):
                info("* " + pkg.name)
            else:
                info("  " + pkg.name)


@cache.command()
def clear():
    """Removes all packages from the cache"""
    with console.status("[bold green]Preparing") as status:
        for pkg in CACHE_DIR.iterdir():
            status.update(f"[bold green]Removing {pkg.name}")
            try:
                shutil.rmtree(pkg)
            except OSError as e:
                console.print(f"[red]Failed to remove package. {e}")
                return
            else:
                _debug(f"OK - {pkg.name}")
        else:
            console.print(f"[green]Ok")


@cache.command()
@click.argument("pkg_name", required=True, type=str, nargs=1)
def update(pkg_name: str):
    """Updates the locally cloned repository of a package"""
    pkg_name = pkg_name.lower()
    with console.status("[bold green]Preparing") as status:
        pkg_path = CACHE_DIR / pkg_name
        if not dir_exists(CACHE_DIR / pkg_name):
            error(f"[red]Package {pkg_name} does not exist in cache.")
            return

        status.update(f"[bold green]Updating {pkg_name}")
        try:
            result = subprocess.run(
                ("git", "pull"),
                cwd=pkg_path,
                capture_output=True,
                encoding=sys.stdout.encoding,
            )
            _debug("STDOUT:")
            _debug(result.stdout)
            _debug("\nSTDERR:")
            _debug(result.stderr)
            result.check_returncode()
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to update repository. {e}")
            return
        else:
            console.print(f"[green]Ok")


@cache.command()
@click.argument("pkg_name", required=True, type=str, nargs=1)
def remove(pkg_name: str):
    """Removes a package from the cache"""
    pkg_name = pkg_name.lower()
    with console.status("[bold green]Preparing") as status:
        pkg_path = CACHE_DIR / pkg_name
        if not pkg_path.exists():
            console.print(f"[red]Package {pkg_name} does not exist in cache.")
            return
        status.update("[bold green]Removing directory")
        try:
            shutil.rmtree(pkg_path)
        except OSError as e:
            console.print(f"[red]Failed to remove package. {e}")
            return
        else:
            console.print(f"[green]Ok")


@main.command()
@click.option("--brief", "-B", is_flag=True, help="Compacts output")
@click.argument("pkg_name", required=True, type=str, nargs=1)
def search(brief: bool, pkg_name: str):
    """Searches for a package on the AUR"""
    with console.status("[bold green]Searching") as status:
        try:
            response = session.get(
                "https://aur.archlinux.org/rpc/v5/search/" + pkg_name
            )
            _debug(f"Response ({response.status_code}): {response.json()}")
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            error(f"[red]Failed to download {pkg_name} metadata. {e}")
            return

        data = response.json()
        status.update(f"Displaying {data['resultcount']:,} results")
        for result in sorted(data["results"], key=lambda _e: _e['Popularity']):
            console.print(
                "[cyan]{0[Name]}[/] (v{0[Version]}, {1} popularity)".format(
                    result,
                    round(result['Popularity'], 2)
                )
            )
            if brief is False:
                console.print("\t" + repr(result["Description"].splitlines()[0]), markup=False)
                console.print()


@main.command()
@click.argument("pkg_names", required=True, type=str, nargs=-1)
@click.pass_context
def build(ctx: click.Context, pkg_names: Tuple[str]):
    """Builds packages, preparing them for install."""
    ok = []
    nok = []
    for pkg_name in pkg_names:
        pkg_name = pkg_name.lower()
        pkg_dir = CACHE_DIR / pkg_name
        if not dir_exists(pkg_dir):
            error(f"Package {pkg_name} is not cached locally. Did you run `nayur cache get {pkg_name}`?")
            continue

        info(f"Running makepkg -s -f --noconfirm in {pkg_dir}")
        try:
            result = subprocess.run(
                (
                    "makepkg",
                    "-s",
                    "-f",
                    "--noconfirm"
                ),
                cwd=pkg_dir
            )
            result.check_returncode()
        except subprocess.CalledProcessError:
            nok.append(pkg_name)
            return
        else:
            if ctx.obj["DEBUG"] is False:
                os.system("clear")
            ok.append(pkg_name)

    for pkg_name in ok:
        info("Ok - " + pkg_name)

    for pkg_name in nok:
        error("Failed - " + pkg_name)


@main.command()
@click.argument("pkg_names", required=True, type=str, nargs=-1)
@click.pass_context
def install(ctx: click.Context, pkg_names: Tuple[str]):
    """Installs a package"""
    ok = []
    nok = []
    for pkg_name in pkg_names:
        pkg_name = pkg_name.lower()
        pkg_dir = CACHE_DIR / pkg_name
        if not dir_exists(pkg_dir):
            _debug(f"Package {pkg_name} is not cached locally. Did you run `nayur cache get {pkg_name}`?")
            continue

        pattern = f"*-{platform.machine()}.pkg.tar.zst"
        _debug("Looking for build files with pattern: " + repr(pattern))
        files = glob.glob(pattern, root_dir=pkg_dir)
        _debug(f"Detected build files: {', '.join(files)}")
        files = sorted(files, key=lambda file: (pkg_dir / file).stat().st_mtime_ns, reverse=True)
        if not files:
            _debug(f"No build files detected for {pkg_name}. Did you run `nayur build {pkg_name}`?")
            nok.append(pkg_name)
            continue
        for target_file in files:
            path = pkg_dir / target_file
            info(f"Trying {path}")
            try:
                result = subprocess.run(
                    (
                        "sudo",
                        "pacman",
                        "-U",
                        "--noconfirm",
                        str(path.absolute())
                    )
                )
                result.check_returncode()
                _debug(f"Command: {' '.join(result.args)}")
                _debug(f"Return code: {result.returncode}")
            except subprocess.CalledProcessError:
                warn(f"Failed on {target_file}")
                continue
            else:
                os.remove(path)
                ok.append(pkg_name)
                break
        else:
            nok.append(pkg_name)

    if ctx.obj["DEBUG"] is False:
        os.system("clear")
    for pkg_name in ok:
        info("Ok - " + pkg_name)

    for pkg_name in nok:
        error("Failed - " + pkg_name)


if __name__ == "__main__":
    main()
