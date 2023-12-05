# SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=missing-function-docstring

""" setup.py for setuptools """

import os.path
import setuptools


def project_path(*names):
    return os.path.join(os.path.dirname(__file__), *names)


with open(project_path("VERSION"), encoding="utf-8") as f:
    version = f.read().strip()

requires = [
    "colorlog",
    "gitpython",
    "pandas",
    "tabulate",
]

setuptools.setup(
    name="ghafscan",
    version=version,
    description="Run and summarize vulnerability scans",
    author="TII",
    author_email="henri.rosten@unikie.com",
    python_requires=">=3.8",
    install_requires=requires,
    license="Apache-2.0",
    classifiers=[  # See:https://pypi.org/classifiers/
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=setuptools.find_namespace_packages(where="src"),
    package_dir={"": "src"},
    package_data={"ghafscan.templates": ["*.md"]},
    entry_points={
        "console_scripts": [
            "ghafscan = ghafscan.main:main",
        ]
    },
)
