from pyramid.view import view_config
import json
import requests


@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    queryNodes = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX owl: <http://www.w3.org/2002/07/owl#>        
        SELECT ?from ?to
        WHERE {
        ?child rdfs:subClassOf ?n . ?n owl:onProperty <http://purl.obolibrary.org/obo/RO_0002202> ; owl:someValuesFrom ?parent . 
        ?parent rdfs:label ?from .
        ?child rdfs:label ?to .
        } """
    headers = {'content-type' : 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    myparam = { 'query': queryNodes }
    endpoint = "http://localhost:80/hdev/sparql"
    r=requests.get(endpoint,myparam,headers=headers)    
    search = r.json()
    suggestions=[]
    for row in search["results"]["bindings"] :
        dict =  {}
        for elt in search["head"]["vars"] : 
            if elt in row :
                dict[elt] = row[elt]["value"] 
        dict["weight"] = 1  
        suggestions.append(dict)
    jsond = json.loads(json.dumps(suggestions))

    return {'project': 'ontoviewer', 'jsond':jsond}
