import traceback
from datetime import datetime

import jinja2
from flask import Flask, render_template, request
from flask_cors import CORS
import logging.config

from fastergerman.i18n import I18n, UNEXPECTED_ERROR
from fastergerman.web import RequestData, ValidationError, WebApp

# AWS elastic beanstalk requires that we name this `application`, not `app` or any other thing.
# AWS elastic beanstalk requires that the app be fully initialized in the global scope.
# (in particular, not within the main block below).
print(f"{datetime.now()} | Flask(__name__)")
application = Flask(__name__)
CORS(application)

app: WebApp = WebApp(application)
logging.config.dictConfig(app.logging_config.to_dict())

INDEX_TEMPLATE = 'index.html'
PREPOSITION_TRAINER = '/preposition-trainer'
PREPOSITION_TRAINER_INDEX_TEMPLATE = f'{PREPOSITION_TRAINER}/index.html'[1:]


@application.template_filter('url_quote')
def url_quote_filter(s):
    return jinja2.utils.url_quote(s)


def _handle_exception(message):
    print(traceback.format_exc())
    data = app.web_service.default()
    if request.path.startswith(PREPOSITION_TRAINER):
        template = PREPOSITION_TRAINER_INDEX_TEMPLATE
    else:
        template = INDEX_TEMPLATE
    data["error"] = message
    return render_template(template, **data), 400


@application.errorhandler(Exception)
def handle_exception(_):
    lang_code = RequestData.get_language_code(request)
    return _handle_exception(I18n.translate(lang_code, UNEXPECTED_ERROR))


@application.errorhandler(ValidationError)
def handle_validation_error(e):
    return _handle_exception(e.message)


@application.route('/')
def index():
    data = RequestData.collect(request)
    return render_template(INDEX_TEMPLATE, **app.web_service.default(data))


@application.route(PREPOSITION_TRAINER, methods=['GET', 'POST'])
def preposition_trainer():
    data = RequestData.preposition_trainer(request)
    return render_template(PREPOSITION_TRAINER_INDEX_TEMPLATE,
                           **app.web_service.preposition_trainer(data))


if __name__ == '__main__':
    print(f"{datetime.now()} | __main__")
    app.start()
