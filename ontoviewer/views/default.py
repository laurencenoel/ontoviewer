from pyramid.view import view_config
import json
import requests


@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    if ($request_method = 'POST') {
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range';
     }


    return {'project': 'ontoviewer'}
