#!/usr/bin/env python
"""Setup script for the project."""

import io
import os
import re

from setuptools import find_packages, setup


INSTALL_REQUIRES = ["click", "colorclass", "sphinx>5"]
LICENSE = "MIT"
NAME = "sphinxcontrib-versioning"


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8"),
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


VERSION = find_version("sphinxcontrib_versioning", "__init__.py")
readme = read("README.rst")


if __name__ == "__main__":
    setup(
        author="PyTorch-Ignite Team",
        author_email="contact@pytorch-ignite.ai",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Framework :: Sphinx :: Extension",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: MacOS",
            "Operating System :: POSIX :: Linux",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: Implementation :: PyPy",
            "Topic :: Documentation :: Sphinx",
            "Topic :: Software Development :: Documentation",
        ],
        description="Sphinx extension that allows building versioned docs for PyTorch-Ignite",
        entry_points={
            "console_scripts": [
                "sphinx-versioning = sphinxcontrib_versioning.__main__:cli"
            ]
        },
        install_requires=INSTALL_REQUIRES,
        keywords="sphinx versioning versions version branches tags",
        license=LICENSE,
        long_description=readme,
        name=NAME,
        package_data={
            "": [
                os.path.join("_static", "banner.css"),
                os.path.join("_templates", "banner.html"),
                os.path.join("_templates", "layout.html"),
                os.path.join("_templates", "versions.html"),
            ]
        },
        packages=find_packages(exclude=("tests", "tests.*")),
        url="https://github.com/pytorch-ignite/{NAME}/",
        version=VERSION,
        zip_safe=False,
    )
