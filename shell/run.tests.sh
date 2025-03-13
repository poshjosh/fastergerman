#!/usr/bin/env bash

source ./pre_run.sh

printf "\nStarting unit tests\n\n"

python3 -m unittest discover -s test -p "*test.py"