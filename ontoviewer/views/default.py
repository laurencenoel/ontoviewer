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
    endpoint = "http://localhost:8080/rdf4j-server/repositories/hcao"

    querystr = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
         PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>  
        PREFIX model: <http://purl.amypdb.org/model/> 
        PREFIX thes: <http://purl.amypdb.org/thesaurus/> 
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        PREFIX hsapdv: <http://purl.obolibrary.org/obo/hsapdv#>
        SELECT distinct ?CS ?label ?startDay ?comment 
        WHERE {
        ?CS rdfs:subClassOf obo:HsapDv_0000000 .
        ?CS rdfs:label ?label .
        FILTER regex(str(?label), "Carnegie","i") 
        ?CS hsapdv:start_dpf ?startDay .
        OPTIONAL{ ?CS rdfs:comment ?comment . }
       } ORDER BY ?startDay
  """
    headers = {'content-type' : 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    myparam = { 'query': querystr }
    r=requests.get(endpoint,myparam,headers=headers)    
    results = r.json()
      
    data=[]
    for row in results["results"]["bindings"] :
        dict =  {}
        for elt in results["head"]["vars"] : 
            if elt in row :
                dict[elt] = row[elt]["value"] 
            else : 
                dict[elt] = ""
        data.append(dict)
     
    dicoCS  = {}
    for i,elt in enumerate(data) : 
        nbDay = int(float(elt["startDay"]))
        if nbDay == 0 : 
            nbDay = 1
        dicoInfo = {}
        dicoInfo["label"] = elt["label"]
        dicoInfo["comment"] = elt["comment"]
        if i < len(data) : 
            dicoInfo["duration"] = int(float(data[i+1]["startDay"])) - nbDay
        else : 
            dicoInfo["duration"] = 1
        dicoCS[nbDay] = dicoInfo
     
    otherStage = {}
    otherStage[1] = [1,""]
    otherStage[2] = [2,"Cleavage stage and morula stage",""]
    otherStage[4] = [9,"Blastula stage", "Embryonic stage that is an early stage of embryonic development in animals and is produced by cleavage of a fertilized ovum, with formation of a central fluid-filled cavity called the blastocoel"]
    otherStage[13] = [2,"Gastrula stage", "Embryonic stage defined by a complex and coordinated series of cellular movements that occurs at the end of cleavage"]
    otherStage[15] = [4,"Neurula stage", "Embryonic stage defined by the formation of a tube from the flat layer of ectodermal cells known as the neural plate."]
    otherStage[19] = [37,"Organogenesis stage", "Embryonic stage at which the ectoderm, endoderm, and mesoderm develop into the internal organs of the organism"]
    otherStage[56] = [210, "Fetal stage","Prenatal development is a continuum, with no clear defining feature distinguishing an embryo from a fetus. The use of the term 'fetus' generally implies that a mammalian embryo has developed to the point of being recognizable as belonging to its own species, though the point at which this occurs is subjective."]
    
        
    return {'project': 'ontoviewer', 'carnegie_stages':data, 'other_stages' : otherStage}
