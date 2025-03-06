#!/usr/bin/env bash

source ./pre_run.sh

printf "\nStarting end-to-end tests\n\n"

npm run cy:test

APP_PORT=5010

# Kill all python processes on the specified port
kill -9 `lsof -i :${APP_PORT} | grep Python | awk '{print $2}'`

printf "\nIf the kill process fails, check that the port is %d\n\n" "${APP_PORT}"

# Kill all python processes
#kill -9 `ps -ef | awk '/[P]ython/{print $2}'`

