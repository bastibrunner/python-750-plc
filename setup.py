"""Setup for the wg750xxx module."""

import setuptools

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wg750xxx",
    version="0.1.0",
    author="Sebastian",
    author_email="your.email@example.com",
    description="Python module for interacting with WAGO 750 series PLCs through Modbus TCP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/python-wg750xxx",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/python-wg750xxx/issues",
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
        "pymodbus",
        "pyyaml",
    ],
)
