#!/usr/bin/env bash

cd ../src || exit 1

export APP_INPUT_NAME=${APP_INPUT_NAME:-combo_trainer}
export APP_INPUT_TEXT=${APP_INPUT_TEXT:-Combined Trainer}
export APP_INPUT_LANG=${APP_INPUT_LANG:-en}
export APP_TRANSLATIONS_DIR=${APP_TRANSLATIONS_DIR:-resources/config/i18n}

export PYTHONUNBUFFERED=1

python3 translator.py

