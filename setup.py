#!/usr/bin/env python

from setuptools import setup, find_packages  # type: ignore

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    author="Aleksandar Mitev @ SunStrong Management",
    author_email="amitev@sunstrongmanagement.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
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
    url="https://github.com/SunStrong-Management/pypvs.git",
    version="0.1.1",
    zip_safe=False,
)
