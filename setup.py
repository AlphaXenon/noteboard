import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Package Meta-Data
NAME = "noteboard"
DESCRIPTION = "Manage your notes & tasks in a tidy and fancy way."
URL = "https://github.com/a1phat0ny/noteboard"
EMAIL = "tony.chan2342@gmail.com"
AUTHOR = "a1phat0ny"
REQUIRES_PYTHON = ">=3.6.0"
REQUIRED = [
    "colorama"
]
about = {}
with open(os.path.join(here, NAME, "__version__.py"), "r") as f:
    exec(f.read(), about)

long_description = \
"""
Noteboard lets you manage your notes & tasks in a tidy and fancy way.

## Features

* Fancy interface ✨
* Simple & Easy to use 🚀
* Fast as lightning ⚡️
* Manage notes & tasks in multiple boards 🗒
* Run item as command inside terminal (subprocess) 💨
* Tag item with color and text 🏷
* Import boards from external JSON files & Export boards as JSON files
* Undo multiple actions / changes
* Interactive mode for dynamic operations with auto-complete and auto-suggestions
* `Gzip` compressed storage 📚
* Configurable through `~/.noteboard.json`
"""

# Setup
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    entry_points={
        "console_scripts": ["board=noteboard.cli:main"],
    },
    install_requires=REQUIRED,
    include_package_data=True,
    packages=find_packages(),
    license="MIT",
    keywords=["cli", "todo", "task", "note", "board", "gzip", "interactive", "taskbook"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
    ],
)
