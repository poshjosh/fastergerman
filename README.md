# [fastergerman](http://fastergerman.us-east-2.elasticbeanstalk.com/)

### Learn the German language faster

Learn german faster with multi-choice trainers. 

There could be trainers for various language constructs. For example: 
`preposition`, `verb`, `noun`, `adjective`, etc.

See the various trainers [here](./docs/trainers/index.md)

### Usage

Visit the [fastergerman website](http://fastergerman.us-east-2.elasticbeanstalk.com/)

### Local use

#### Requirements

- Python 3.9 or higher

#### Installation

- Run `shell/install.sh`

#### Run

- Run `shell/run.sh`

#### Tests

- Tests - run `shell/run.tests.sh`
- End-to-end tests - `shell/run.e2e.tests.sh`

#### i18n

- You can add translations by running the script `shell/add-translations.sh`
- By default translations are located in the `src/resources/config/i18n` directory.
- The location of translations can be changed by setting either the `APP_TRANSLATIONS_DIR` 
environment variable, or specifying the `app:translations:dir` in the 
`src/resources/config/app.yaml` file.

