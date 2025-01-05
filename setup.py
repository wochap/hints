import codecs
import os
import re

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


dynamic_version = find_version("hints", "__init__.py")

setup(
    name="hints",
    version=dynamic_version,
    author="Alfredo Sequeida",
    description="Hints lets you navigate GUI applications in Linux without your"
    ' mouse by displaying "hints" you can type on your keyboard to interact'
    " with GUI elements.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlfredoSequeida/hints",
    download_url="https://github.com/AlfredoSequeida/hints/archive/"
    + dynamic_version
    + ".tar.gz",
    python_requires=">=3.10",
    keywords=[
        "vim",
        "vimium",
        "hints",
        "mouseless",
        "keyboard",
        "keyboard navigation",
        "linux",
        "x11",
        "wayland",
    ],
    platforms="any",
    classifiers=[
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment",
        "Topic :: Desktop Environment :: Window Managers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
    ],
    license="GPLv3",
    packages=["hints", "hints.backends", "hints.huds"],
    include_package_data=True,
    install_requires=["PyGObject", "pynput", "pillow", "opencv-python"],
    entry_points={"console_scripts": ["hints = hints.hints:main"]},
)
