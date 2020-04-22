from pyramid.view import view_config
import json


@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    data =  """[
        {from: "Canada",  to: "France",  weight: 1},
        {from: "Canada",  to: "Germany", weight: 1},
        {from: "Canada",  to: "Italy",   weight: 1},
        {from: "Canada",  to: "Spain",   weight:  1},
        {from: "USA",     to: "France",  weight:  1},
        {from: "USA",     to: "Germany", weight: 1},
        {from: "USA",     to: "Spain",   weight: 1}
    ]"""
    return {'project': 'ontoviewer', 'jsond':json.load(data)}
