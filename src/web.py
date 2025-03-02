import jinja2
from flask import Flask, render_template, request
from flask_cors import CORS
import logging.config

from fastergerman.app import App
from fastergerman.config import WebAppConfig
from fastergerman.file import load_yaml
from fastergerman.web import RequestData, ValidationError, WebService, GameService

web_app = Flask(__name__)
CORS(web_app)


INDEX_TEMPLATE = 'index.html'
PREPOSITION_TRAINER = '/preposition-trainer'
PREPOSITION_TRAINER_INDEX_TEMPLATE = f'{PREPOSITION_TRAINER}/index.html'[1:]


@web_app.template_filter('url_quote')
def url_quote_filter(s):
    return jinja2.utils.url_quote(s)


@web_app.errorhandler(ValidationError)
def handle_validation_error(e):
    if request.path.startswith(PREPOSITION_TRAINER):
        template = PREPOSITION_TRAINER_INDEX_TEMPLATE
        data = RequestData.preposition_trainer_config(request, False)
        data = web_service.with_game_session(
            data, web_service.get_game_service().get_or_create_session(data))
    else:
        template = INDEX_TEMPLATE
        data = web_service.index()
    data["error"] = e.message
    return render_template(template, **data), 400


@web_app.route('/')
def index():
    return render_template(INDEX_TEMPLATE, **web_service.index())


@web_app.route(PREPOSITION_TRAINER)
def preposition_trainer():
    data = RequestData.preposition_trainer_config(request)
    return render_template(PREPOSITION_TRAINER_INDEX_TEMPLATE,
                           **web_service.preposition_trainer(data))

if __name__ == '__main__':

    logging.config.dictConfig(load_yaml('resources/config/logging.yaml'))

    app_config = WebAppConfig(load_yaml('resources/config/app.yaml'))

    web_service = WebService(app_config, GameService())

    App.add_shutdown_callback(web_service.close)

    web_app.run(
        host='0.0.0.0',
        port=app_config.get_web_port(),
        debug=app_config.is_production() is False)

