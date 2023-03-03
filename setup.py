import subprocess
from os import getenv
from pathlib import Path
from setuptools import setup

base_version = getenv("NAYUR_BUILD_VERSION", "0.1.0a1")
if getenv("NAYUR_RELEASE", "0") == "1":
    version = base_version
else:
    _commit = subprocess.run(("git", "rev-list", "--count", "HEAD"), capture_output=True, encoding="utf-8").stdout
    _commit = _commit.strip()
    version = f"{base_version}.dev{_commit}"

setup(
    name='nayur',
    version=version,
    packages=['src'],
    url='https://github.com/EEKIM10/nayur',
    license='GLP3',
    author='nex',
    author_email='packages@nexy7574.co.uk',
    description='The least helpful AUR helper',
    entry_points={
        'console_scripts': [
            'nayur = src.main:main'
        ]
    },
    install_requires=Path('requirements.txt').read_text().splitlines(),
    python_requires='>=3.9',
)
