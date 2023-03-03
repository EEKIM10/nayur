import typing
import requests
import time
import re
import logging

from .out import warn, debug


def find_deps(
        *packages: str,
        recursive: bool = True,
        optional: bool = True,
        make: bool = True,
        **kw
) -> typing.Set[str] | None:
    """Finds all dependencies from the AUR."""
    found = kw.pop("found", set())
    level = kw.pop("level", 0)
    level += 1

    try:
        url = f"https://aur.archlinux.org/rpc/v5/info?arg[]={'&arg[]='.join(packages)}"
        # debug("GET " + url)
        response = requests.get(
            url
        )
        # debug("HTTP %s %s" % (response.status_code, response.reason))
        # debug(response.text)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        warn(f"Failed to check for dependencies: {e}")
    else:
        for pkg in response.json()["results"]:
            found.add(pkg["Name"])
            if recursive:
                time.sleep(level // 10 * 0.075)
                to_check = pkg.get("Depends", [])
                if optional:
                    to_check += pkg.get("OptDepends", [])
                if make:
                    to_check += pkg.get("MakeDepends", [])

                for dep in to_check.copy():
                    to_check.remove(dep)
                    # remove any version identifiers
                    dep = re.sub(r"([<>=]+.*)", "", dep)
                    # remove any arch identifiers
                    dep = re.sub(r"(\[.*\])", "", dep)
                    to_check.append(dep)

                to_check = set(to_check)
                debug(f"Found {len(to_check)} dependencies of {pkg['Name']} (pre-filter): {to_check}")
                to_check -= found
                debug(f"Found {len(to_check)} dependencies of {pkg['Name']} (post-filter): {to_check}")

                debug(
                    f"Recursively checking for {len(to_check)} dependencies of {pkg['Name']}: {to_check}"
                )
                found = find_deps(*to_check, found=found, recursive=recursive, level=level)

            debug("\n\nDependencies to clone for %s: %s" % (packages, ", ".join(found)))
        return found


def check_deps(deps: typing.Iterable[str]) -> typing.Set[str] | None:
    deps = set(deps)
    try:
        debug(f"Checking for {len(deps)} in AUR: {deps}")
        _x = "&".join(f"arg[]={c}" for c in deps)
        response = requests.get(
            f"https://aur.archlinux.org/rpc/v5/info?{_x}"
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        warn(f"Failed to check for dependencies: {e}")
    else:
        x = set()

        for pkg in response.json()["results"]:
            x.add(pkg["Name"])
        debug(f"Found {len(x)} AUR dependencies: {x}")
        return x
