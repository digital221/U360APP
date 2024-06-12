from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in unify360/__init__.py
from unify360 import __version__ as version

setup(
	name="unify360",
	version=version,
	description="Unify 360",
	author="CodesSoft",
	author_email="shahid@codessoft.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
