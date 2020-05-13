from pyramid.view import view_config
import json
import requests
from pyramid.events import NewResponse, subscriber

@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):



    return {'project': 'ontoviewer'}



@subscriber(NewResponse)
def add_cors_headers(event):
    if event.request.is_xhr:
        event.response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET',
        })