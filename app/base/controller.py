from flask import request
from flask_restful import Resource
from app.helpers.functions import log_error as le, get_version

class BaseController():
    def __init__(self, **kwargs):
        self.logger_name = __name__
        self.ver = get_version()
        self.module = ''
        self.endpoint = ''

    def get_endpoint(self, name):
        self.endpoint = f'{self.ver}-{self.module}-{name}'
        return self.endpoint
    
    def check_endpoint(self, name):
        return request.endpoint == self.get_endpoint(name)
    
    def log_error(self, exception, name=None, exec_info=False):
        logger_name = name or self.endpoint
        le(exception, logger_name, exec_info=exec_info)

class DefaultController(Resource):
    def get(self):
        return {'method': 'get'}, 200
    
    def put(self):
        return {'method': 'put'}, 200
    
    def post(self):
        return {'method': 'post'}, 200
    
    def delete(self):
        return {'method': 'delete'}, 200