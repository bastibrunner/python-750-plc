"""Setup for the wg750xxx module."""

from pathlib import Path

import setuptools

with Path("README.md").open("r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-750-plc",
    version="0.2.5",
    author="Bastian Brunner",
    author_email="bb@intern-net.de",
    description="Python module for interacting with WAGO 750 series PLCs through Modbus TCP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bastibrunner/python-750-plc",
    project_urls={
        "Bug Tracker": "https://github.com/bastibrunner/python-750-plc/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Home Automation",
        "Topic :: System :: Hardware",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "numpy>=2.2.2",
        "pydantic>=2.10.6",
        "pymodbus>=3.8.3",
    ],
)
