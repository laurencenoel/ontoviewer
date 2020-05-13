from pyramid.view import view_config
import json
import requests
from pyramid.events import NewResponse, subscriber

@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    return {'project': 'ontoviewer'}

