#!/usr/bin/env python

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(name="automate-idea-to-social",
          version="0.0.1",
          description="Learn German faster",
          author="PoshJosh",
          author_email="posh.bc@gmail.com",
          install_requires=[],
          license="MIT",
          classifiers=[
              "Programming Language :: Python :: 3",
              "License :: OSI Approved :: MIT License",
              "Operating System :: OS Independent",
          ],
          url="https://github.com/poshjosh/fastergerman",
          packages=find_packages(
              where='src',
              include=['fastergerman', 'fastergerman.*'],
              exclude=['test', 'test.*']
          ),
          package_dir={"": "src"},
          )
