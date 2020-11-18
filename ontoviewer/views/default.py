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

@view_config(route_name='cells_precursor', renderer='../templates/cells_precursor.jinja2')
def cells_precursor(request):    
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
        SELECT ?CS ?label ?startDay ?comment ?EHDAACS
        WHERE {
        ?CS rdfs:subClassOf obo:HsapDv_0000000 .
        ?CS rdfs:label ?label .
        FILTER regex(str(?label), "Carnegie","i") 
        ?CS hsapdv:start_dpf ?startDay .
        OPTIONAL{ ?CS rdfs:comment ?comment . }
        OPTIONAL{
        ?CS oboInOwl:hasDbXref ?CSref .
        FILTER regex(str(?CSref), "EHDA", "i")
        BIND (IRI(CONCAT("http://purl.obolibrary.org/obo/ehdaa2#",strafter(?CSref,":"))) AS ?EHDAACS) }
       }  ORDER BY ?startDay
  """
  
      #to get the cells/organs appearing a that stage
    querystr2 = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
         PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>  
        PREFIX model: <http://purl.amypdb.org/model/> 
        PREFIX thes: <http://purl.amypdb.org/thesaurus/> 
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        PREFIX hsapdv: <http://purl.obolibrary.org/obo/hsapdv#>
        SELECT ?EHDAACS (GROUP_CONCAT(DISTINCT ?eltInfo; SEPARATOR="||") AS ?eltList)
        WHERE {
        ?restrictedClass owl:someValuesFrom ?EHDAACS ; owl:onProperty <http://purl.obolibrary.org/obo/BFO_0000068> .
        ?element rdfs:subClassOf ?restrictedClass .
        ?element rdfs:label ?labelElt .
        ?element oboInOwl:id ?labelId .
        BIND (CONCAT(?labelElt,"|",?labelId) AS ?eltInfo)
       } GROUP BY ?EHDAACS
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
     

    myparam2 = { 'query': querystr2 }
    r2=requests.get(endpoint,myparam2,headers=headers)    
    results2 = r2.json()
      
    data2=[]
    for row in results2["results"]["bindings"] :
        dict =  {}
        for elt in results2["head"]["vars"] : 
            if elt in row :
                dict[elt] = row[elt]["value"] 
            else : 
                dict[elt] = ""
        data2.append(dict)
    
    dictCS = {}
    for elt in data2 :
        dictCS[elt["EHDAACS"]] = elt["eltList"]
    
    dictCS2 = {}
    for key,value in dictCS.items() : 
        if key.endswith("a") or key.endswith("b") or key.endswith("c") : 
            newkey = key[:-1]
            if newkey in dictCS2.keys() : 
                value2 = dictCS2[newkey]
                dictCS2[newkey] = value2 + "||" + value
            else : 
                dictCS2[newkey] = value                
        else : 
            dictCS2[key] = value
    
    dicoCS  = {}
    for i,elt in enumerate(data) : 
        nbDay = int(float(elt["startDay"]))
        if nbDay == 0 : 
            nbDay = 1
        dicoInfo = {}
        dicoInfo["label"] = elt["label"]
        dicoInfo["comment"] = elt["comment"]
        ehdaa = elt["EHDAACS"]
        
        eltL2 = []
        for key,value in dictCS2.items() : 
            if ehdaa == key :                 
                eltL = value.split("||")
                for item in eltL : 
                    nom = item.split("|")[0]
                    identifier = item.split("|")[1]
                    idForUrl = identifier.replace(":","_")
                    link="<a href='https://www.ebi.ac.uk/ols/ontologies/ehdaa2/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F"+idForUrl+"'>"+nom+"</a>"
                    eltL2.append(link)
        dicoInfo["eltList"] = eltL2
        if i < len(data) -1 : 
            dicoInfo["duration"] = int(float(data[i+1]["startDay"])) - nbDay
        else : 
            dicoInfo["duration"] = 1
        dicoCS[nbDay] = dicoInfo
    
    dicoCS[57] = {"label":"", "comment":"", "duration":56, "eltList":""}
     
    otherStage = {}
    otherStage[1] = [1,""]
    otherStage[2] = [2,"Cleavage stage and morula stage",""]
    otherStage[4] = [9,"Blastula stage", "Embryonic stage that is an early stage of embryonic development in animals and is produced by cleavage of a fertilized ovum, with formation of a central fluid-filled cavity called the blastocoel"]
    otherStage[13] = [2,"Gastrula stage", "Embryonic stage defined by a complex and coordinated series of cellular movements that occurs at the end of cleavage"]
    otherStage[15] = [4,"Neurula stage", "Embryonic stage defined by the formation of a tube from the flat layer of ectodermal cells known as the neural plate."]
    otherStage[19] = [38,"Organogenesis stage", "Embryonic stage at which the ectoderm, endoderm, and mesoderm develop into the internal organs of the organism"]
    otherStage[57] = [56, "Fetal stage","Prenatal development is a continuum, with no clear defining feature distinguishing an embryo from a fetus. The use of the term 'fetus' generally implies that a mammalian embryo has developed to the point of being recognizable as belonging to its own species, though the point at which this occurs is subjective."]
    
        
    return {'project': 'ontoviewer', 'carnegie_stages':dicoCS, 'other_stages' : otherStage}
