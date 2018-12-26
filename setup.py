import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Package Meta-Data
NAME = "noteboard"
DESCRIPTION = "Manage your notes & tasks in a tidy and fancy way."
URL = "https://github.com/AlphaXenon/noteboard"
EMAIL = "tony.chan2342@gmail.com"
AUTHOR = "AlphaXenon"
REQUIRES_PYTHON = ">=3.6.0"
REQUIRED = [
    "colorama"
]
about = {}
with open(os.path.join(here, NAME, "__version__.py"), "r") as f:
    exec(f.read(), about)

with open(os.path.join(here, "README.md")) as f:
    long_description = "\n" + f.read()

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
        "console_scripts": ["board=noteboard.main:main"],
    },
    install_requires=REQUIRED,
    include_package_data=True,
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
    ],
)