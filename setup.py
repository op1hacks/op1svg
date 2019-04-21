#!/usr/bin/env python3
import re
from setuptools import setup


version = re.search(
    "^__version__\s*=\s*\"([^\"]*)\"",
    open("op1svg/main.py").read(),
    re.M
    ).group(1)


setup(name="op1svg",
      version=version,
      description="Normalize SVG files so that the OP-1 understands them.",
      author="Richard Lewis",
      author_email="richrd.lewis@gmail.com",
      url="https://github.com/op1hacks/op1svg/",
      packages=["op1svg"],
      install_requires=[
          "svg.path",
      ],
      entry_points={
          "console_scripts": ["op1svg=op1svg.main:main"]
      },
      classifiers=[]
      )
