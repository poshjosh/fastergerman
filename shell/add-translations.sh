#!/usr/bin/env bash

cd ../src || exit 1

export APP_INPUT_NAME=${APP_INPUT_NAME:-}
export APP_INPUT_TEXT=${APP_INPUT_TEXT:-}
export APP_INPUT_LANG=${APP_INPUT_LANG:-en}
export APP_TRANSLATIONS_DIR=${APP_TRANSLATIONS_DIR:-resources/config/i18n}

export PYTHONUNBUFFERED=1

python3 translator.py

