#!/usr/bin/env bash

source ./pre_run.sh

if [ "$WEB_APP" = true ] || [ "$WEB_APP" = "true" ] ; then
  printf "\nStarting web app\n\n"
  python3 web.py
else
  printf "\nStarting app\n\n"
  python3 main.py
fi
