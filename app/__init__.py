import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from app.connect_database import ConnectModel
from app.helpers.url_converters import RegexConverter, UUIDConverter
from app.urls import URLS

# ============================== API COMMON ============================== #
os.environ['TZ'] = 'UTC'
app = Flask(__name__, static_url_path='/static')
app.secret_key = os.getenv('SECRET_KEY')
CORS(app, supports_credentials=True)
api = Api(app, prefix='')
api.app.config['RESTFUL_JSON'] = {'ensure_ascii': False}

# convert url
app.url_map.converters['regex'] = RegexConverter
app.url_map.converters['uuid'] = UUIDConverter
# Setup URL
for item in URLS:
    api.add_resource(item['resource'], item['url'], **item['kw'])

# Postgres extension
ConnectModel().init_extension()