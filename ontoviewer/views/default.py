from pyramid.view import view_config
import json
import requests
from ontoviewer.utils.Entry import *

@view_config(route_name='home', renderer='../templates/home.jinja2')
def my_view(request):  
    return {'project': 'ontoviewer'}
        

@view_config(route_name='organs', renderer='../templates/organs.jinja2')
def my_view(request):
    itemId = ""
    label = ""
    if 'main_organ' in request.params :
        itemId = request.params['main_organ']
        label = HcaoEntry(itemId).getLabel()   
       
    return {'project': 'ontoviewer', 'label': label, 'itemId' : itemId}