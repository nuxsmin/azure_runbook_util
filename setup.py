import os
import unittest

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def client_test_suite():
    return unittest.TestLoader().discover("tests", pattern="test_*.py")


packages = find_packages()

requires = [
    "adal==1.2.6",
    "pytz==2021.1",
    "msrestazure==0.6.4",
    "pyOpenSSL==20.0.1",
    "azure-mgmt-compute==12.0.0",
    "azure-mgmt-resource==12.0.0"
]

about = {}

with open(os.path.join(here, "azure_runbook_util", "__version__.py"), mode="r", encoding="utf-8") as f:
    exec(f.read(), about)

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    url=about["__url__"],
    license=about["__license__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    description=about["__description__"],
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=packages,
    package_data={"": ["LICENSE", "NOTICE"]},
    package_dir={"azure_runbook_util": "azure_runbook_util"},
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    test_suite="setup.client_test_suite",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.7',
    project_urls={
        "Source": "",
    },
)
