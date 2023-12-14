from .base.controller import DefaultController

URLS = [
    {'resource': DefaultController, 'url': '/', 'kw': {'endpoint': 'default', 'methods': ['GET', 'POST', 'PUT', 'DELETE']}}, 
]