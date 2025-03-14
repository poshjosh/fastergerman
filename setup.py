#!/usr/bin/env python

from setuptools import setup, find_packages

from fastergerman.config import AppConfig
from fastergerman.file import load_yaml
from fastergerman.i18n import I18n, APP_SHORT_DESCRIPTION

if __name__ == "__main__":
    app_config = AppConfig(load_yaml('resources/config/app.yaml'))
    setup(name=app_config.get_app_name(),
          version=app_config.get_app_version(),
          description=I18n.translate_default(APP_SHORT_DESCRIPTION),
          author="PoshJosh",
          author_email="posh.bc@gmail.com",
          install_requires=["PyYAML", "flask", "flask-cors"],
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
