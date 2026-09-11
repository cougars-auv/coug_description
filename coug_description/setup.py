import os
from glob import glob

from setuptools import find_packages, setup

package_name = "coug_description"

setup(
    name=package_name,
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "urdf"), glob("urdf/*.xacro")),
        (
            os.path.join("share", package_name, "urdf/meshes/bluerov2"),
            glob("urdf/meshes/bluerov2/*.*"),
        ),
        (
            os.path.join("share", package_name, "urdf/meshes/wamv"),
            glob("urdf/meshes/wamv/*.*"),
        ),
    ],
    zip_safe=True,
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [],
    },
)
