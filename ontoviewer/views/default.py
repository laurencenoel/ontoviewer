from pyramid.view import view_config
import json
import requests
from ontoviewer.utils.Entry import *

@view_config(route_name='home', renderer='../templates/layout.jinja2')
def my_view(request):  
    return {'project': 'ontoviewer'}
        
@view_config(route_name='organs', renderer='../templates/organs.jinja2')
def my_view(request): 
    return {'project': 'ontoviewer'}

@view_config(route_name='organsId', renderer='../templates/organs.jinja2')
def my_view(request):
    itemId = request.matchdict['itemId']
    label = HcaoEntry(itemId).getLabel()    
    return {'project': 'ontoviewer', 'label': label}