import traceback
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import jinja2
from flask import Flask, render_template, request
from flask_cors import CORS
import logging.config

from werkzeug.exceptions import NotFound

from fastergerman.game.game import NoMoreQuestionsError
from fastergerman.i18n import I18n, UNEXPECTED_ERROR, NOT_FOUND, NO_MORE_QUESTIONS
from fastergerman.web import RequestData, ValidationError, WebApp, TRAINER, CHAT_REQUEST

print(f"{datetime.now()} | Flask({__name__})")

# AWS elastic beanstalk requires that we name this `application`, not `app` or any other thing.
# AWS elastic beanstalk requires that the application be fully initialized in the global scope.
# (in particular, not within the main block below).
application = Flask(__name__)
CORS(application)

app: WebApp = WebApp(application)
logging.config.dictConfig(app.logging_config.to_dict())

INDEX_TEMPLATE = 'index.html'
TRAINERS = '/trainers'
TRAINERS_INDEX_TEMPLATE = f'{TRAINERS}/index.html'[1:]
CHAT = '/chat'
CHAT_INDEX_TEMPLATE = f'{CHAT}/index.html'[1:]

@application.template_filter('url_quote')
def url_quote_filter(s):
    return jinja2.utils.url_quote(s)

@application.template_filter('display_time')
def display_time(timestamp):
    utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return utc.astimezone(ZoneInfo(RequestData.get_timezone(request))).strftime("%d %b - %H:%M:%S")


def _handle_exception(message, template: str = None):
    print(traceback.format_exc())
    data = app.web_service.default()
    if not template:
        if request.path.startswith(TRAINERS):
            template = TRAINERS_INDEX_TEMPLATE
        elif request.path.startswith(CHAT):
            template = CHAT_INDEX_TEMPLATE
        else:
            template = INDEX_TEMPLATE
    data["error"] = message
    return render_template(template, **data), 400


@application.errorhandler(Exception)
def handle_exception(_):
    lang_code = RequestData.get_language_code(request)
    return _handle_exception(I18n.translate(lang_code, UNEXPECTED_ERROR))

@application.errorhandler(NotFound)
def handle_exception(_):
    lang_code = RequestData.get_language_code(request)
    return _handle_exception(I18n.translate(lang_code, NOT_FOUND), "404.html")

@application.errorhandler(ValidationError)
def handle_validation_error(e):
    return _handle_exception(e.message)

@application.errorhandler(NoMoreQuestionsError)
def handle_no_more_questions_error(e):
    lang_code = RequestData.get_language_code(request)
    message = I18n.translate(lang_code, NO_MORE_QUESTIONS, e.total, e.start, e.end)
    return _handle_exception(message)

@application.route('/health')
def health():
    return "ok", 200

@application.route('/')
def index():
    data = RequestData.collect(request)
    return render_template(INDEX_TEMPLATE, **app.web_service.default(data))


@application.route(TRAINERS + '/<path:trainer>', methods=['GET', 'POST'])
def trainers(trainer):
    if not trainer:
        raise NotFound(f"{TRAINER} is required to locate the appropriate trainer.")
    data = RequestData.trainers(request)
    data[TRAINER] = trainer
    return render_template(TRAINERS_INDEX_TEMPLATE, **app.web_service.trainers(data))

@application.route(CHAT, methods=['GET', 'POST'])
def chat():
    data = RequestData.collect(request)
    if CHAT_REQUEST in data:
        data = app.web_service.chat(data)
    else:
        data = app.web_service.default(data)
    return render_template(CHAT_INDEX_TEMPLATE, **data)

if __name__ == '__main__':
    print(f"{datetime.now()} | __main__")
    app.start()
