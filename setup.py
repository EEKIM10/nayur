from pathlib import Path
from setuptools import setup

setup(
    name='nayur',
    version='0.1.0a1',
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
