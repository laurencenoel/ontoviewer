from pyramid.view import view_config
import json
import requests
from ontoviewer.utils.Entry import *

@view_config(route_name='home', renderer='../templates/home.jinja2')
def home(request): 
    return {'project': 'ontoviewer'}
        

@view_config(route_name='organs', renderer='../templates/organs.jinja2')
def organs(request):
    itemId = ""
    label = ""
    if 'main_organ' in request.params :
        itemId = request.params['main_organ']
        label = HcaoEntry(itemId).getLabel()   
       
    return {'project': 'ontoviewer', 'label': label, 'itemId' : itemId}
    
    
@view_config(route_name='organs_comp', renderer='../templates/organs_comp.jinja2')
def organs_comp(request):    
    return {'project': 'ontoviewer'}
    
@view_config(route_name='cells', renderer='../templates/cells.jinja2')
def cells(request):    
    return {'project': 'ontoviewer'}
    
@view_config(route_name='cells_comp', renderer='../templates/cells_comp.jinja2')
def cells_comp(request):    
    return {'project': 'ontoviewer'}

@view_config(route_name='stages', renderer='../templates/stages.jinja2')
def stages(request):    
    return {'project': 'ontoviewer'}
