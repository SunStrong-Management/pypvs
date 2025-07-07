#!/usr/bin/env python

from setuptools import setup, find_packages  # type: ignore

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    author="Sunpower Titanic Orchestra",
    author_email="email@example.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
    description="A Python package that exposes data and commands for a Sunpower PVS6 gateway",
    entry_points={"console_scripts": ["pypvs=pypvs.cli:main",],},
    install_requires=[],
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords="pypvs",
    name="pypvs",
    packages=find_packages(),
    setup_requires=[],
    url="https://github.com/GitHubUser/pypvs",
    version="0.1.0",
    zip_safe=False,
)
