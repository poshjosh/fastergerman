#!/usr/bin/env python

from setuptools import setup, find_packages

from src.fastergerman.config import AppConfig
from src.fastergerman.file import load_yaml

if __name__ == "__main__":
    app_config = AppConfig(load_yaml('src/resources/config/app.yaml'))
    setup(name=app_config.get_app_name(),
          version=app_config.get_app_version(),
          description="Learn german faster",
          author="PoshJosh",
          author_email="posh.bc@gmail.com",
          install_requires=[
              "PyYAML", "flask", "flask-cors", "transformers", "langchain-core", "langgraph>=0.2.28",
              "langchain[groq]", "langchain[openai]", "langchain[anthropic]", "langchain[cohere]",
              "langchain-nvidia-ai-endpoints", "langchain-xai"],
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
