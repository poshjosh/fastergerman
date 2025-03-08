#!/usr/bin/env bash

# See https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html

# After deploying, you can ssh into the EC2 instance and cd `/var/app/current` to see the app files.
# To terminate, from within "$TARGET_DIR" run: `eb terminate "${APP_NAME}-env" --all`

APP_NAME="${APP_NAME:-fastergerman}"
DEPLOY="${DEPLOY:-true}"
TARGET_DIR="${TARGET_DIR:-output/aws}"
ZIP="${ZIP:-true}"

#set -euo pipefail # No need for this in this script, we want logs to show what went wrong

cd .. || exit 1

set -a
source .env
set +a
printf "\nExported environment\n"

if [ -d "$TARGET_DIR" ]; then
  rm -Rf "$TARGET_DIR"
  printf "\nDeleted existing output dir: %s\n" "$TARGET_DIR"
fi

if [ ! -d "$TARGET_DIR" ]; then
  mkdir -p "$TARGET_DIR"
  printf "\nCreated output dir: %s\n" "$TARGET_DIR"
fi

cp -R src/ "${TARGET_DIR}/"

cp src/fastergerman/requirements.txt "${TARGET_DIR}/"

cp .ebignore "${TARGET_DIR}/"
printf "\nCopied files to %s\n" "${TARGET_DIR}/"

# Delete user interface related modules and files
rm "${TARGET_DIR}/main.py"
rm -Rf "${TARGET_DIR}/fastergerman/ui"

rm -Rf "${TARGET_DIR}/fastergerman.egg-info"
rm -Rf "${TARGET_DIR}/output"
rm -Rf "${TARGET_DIR}/test"

printf "\nRemoved directories and files not needed for web app deployment\n"

mv output/aws/web.py "${TARGET_DIR}/application.py"
printf "\nChanged web.py to application.py\n"

cd "${TARGET_DIR}" || exit 1
printf "\nChanged to dir: %s\n" "${TARGET_DIR}"

if [ "$ZIP" = true ] || [ "$ZIP" = "true" ] ; then
  zip -r ../aws.zip .
  printf "\nZipped %s to ../aws.zip\n" "${TARGET_DIR}"
fi

if [ "$DEPLOY" != true ] && [ "$DEPLOY" != "true" ] ; then
  printf "\nSkipping deployment to aws elastic-beanstalk\n"
  exit 0
fi

eb init -p python-3.9 "${APP_NAME}" --region us-east-2
printf "\nInitialized Elastic Beanstalk\n"

# (optional) Run eb init again to configure a default keypair
# so that you can connect to the EC2 instance running your application with SSH:
# Select a key pair if you have one already, or follow the prompts to create a new one.
# If you don't see the prompt or need to change your settings later, run `eb init -i`.
eb init

eb create "${APP_NAME}-env"
printf "\nCreated Elastic Beanstalk environment\n"

function set_eb_env() {
    local key="${1}"
    local val
    val=$(printenv "$key")
    if [[ -z "${val}" ]]; then
      printf "\nNot set, environment variable: %s\n" "${key}"
    else
      eb setenv "${key}=${val}" # "APP_PROFILES=dev" "APP_PORT=5000" "APP_DIR=sessions"
      printf "\nSuccessfully set eb env: %s=%s\n" "$key" "$val"
    fi
}

eb setenv APP_PROFILES=aws,dev
eb setenv APP_PORT=5000
eb setenv APP_DIR=sessions
set_eb_env APP_SECRET_KEY
#set_eb_env APP_LANGUAGE_CODE
#set_eb_env APP_PREPOSITION_TRAINER_QUESTION_SRC

printf "\nOpening deployed environment: %s\n" "${APP_NAME}-env"
eb open "${APP_NAME}-env"
