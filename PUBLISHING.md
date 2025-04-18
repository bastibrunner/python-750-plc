# Publishing to PyPI

This document provides instructions on how to publish the wg750xxx package to PyPI.

## Prerequisites

Make sure you have the necessary tools installed:

```bash
pip install build twine
```

## Build the Package

1. Build the distribution packages:

```bash
python -m build
```

This will create both source distribution and wheel in the `dist/` directory.

## Test the Package on TestPyPI (Recommended)

1. Upload to TestPyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

2. Test the installation from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ wg750xxx
```

## Publish to PyPI

Once you've verified the package works correctly, upload it to the real PyPI:

```bash
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

## Versioning

Remember to update the version number in both `setup.py` and `setup.cfg` before creating a new release. Follow semantic versioning (MAJOR.MINOR.PATCH).

## Cleanup

After successful publishing, you can clean up the build files:

```bash
rm -rf build/ dist/ *.egg-info/
```
