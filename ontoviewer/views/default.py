from pyramid.view import view_config
import json
import requests
from pyramid.events import NewResponse, subscriber

@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    return {'project': 'ontoviewer'}

@view_config(request_method='OPTIONS', permission='options')
def options(self):
    return Response(b'', headerlist=[
        ('Access-Control-Allow-Origin', 'http://localhost:8080'),
        ('Access-Control-Allow-Methods', 'POST'),
        ('Access-Control-Allow-Headers', 'Origin, Content-Type, Accept, Authorization'),
    ])