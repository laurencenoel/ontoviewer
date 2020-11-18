import json, csv
import requests

def getChildren(elt,dico) :
    children = []
    ontoLink = "https://www.ebi.ac.uk/ols/ontologies/cl/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F"
    for key,dicoV in dico.items() : 
        for item in dicoV : 
            if item == elt : 
                children.append(key)
    
    if children == [] : 
        return children
    else : 
        data = []
        for child in children :
            dict = {}
            if "UBERON:" in child : 
                identifier = child.split("|")[0]
                identifier = identifier.replace(":","_")
                dict["uri"] = ontoLink + identifier
            else : 
                dict["uri"] = "#"
            dict["name"] = child.split("|")[1]
            childR = getChildren(child,dico)
            if childR != [] : 
                dict["children"] = childR
            dict["size"] = "1.0"
            data.append(dict)
        return data
            
            
        
                

def humandev_json():
    jsonfile = "../static/humandev_tree.json"      
    ontoLink = "https://www.ebi.ac.uk/ols/ontologies/cl/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F"
        
    enfantParent = {}
        
        #TO DO : child parent List from sparql query
        #?child ?parentList
        
    endpoint = "http://localhost:8080/rdf4j-server/repositories/hcao"

    querystr = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>  
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        PREFIX hsapdv: <http://purl.obolibrary.org/obo/hsapdv#>
        SELECT distinct ?childInfo ?parentInfo
        WHERE {
        ?restrictedClass owl:onProperty <http://purl.obolibrary.org/obo/RO_0002202> ; owl:someValuesFrom ?parent .
        ?parent rdfs:label ?parentLabel .
        ?parent oboInOwl:id ?parentId .
        BIND (CONCAT(?parentId,"|",?parentLabel) AS ?parentInfo)
        ?child rdfs:subClassOf ?restrictedClass .
        ?child rdfs:label ?childLabel .
        ?child oboInOwl:id ?childId .
        BIND (CONCAT(?childId,"|",?childLabel) AS ?childInfo)
       } LIMIT 10
    """
    
    headers = {'content-type' : 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    myparam = { 'query': querystr }
    print("QUERY")
    r=requests.get(endpoint,myparam,headers=headers)    
    results = r.json()
    print("RESULTS")
    data=[]
    for row in results["results"]["bindings"] :
        dict =  {}
        for elt in results["head"]["vars"] : 
            if elt in row :
                dict[elt] = row[elt]["value"] 
            else : 
                dict[elt] = ""
        data.append(dict)
    
    enfantParent = {}
    print("sort child")
    for item in data : 
        if item["childInfo"] in enfantParent.keys() : 
            parent = enfantParent[item["childInfo"]].copy()
            parent.append(item["parentInfo"])
            enfantParent[item["childInfo"]] = parent
        else : 
            enfantParent[item["childInfo"]] = [item["parentInfo"]]
        
                           
    print("get initial Children")
    initialData = []
    initialData.append({"uri":ontoLink + "UBERON_0006603","name":"presumptive mesoderm","children":getchildren("UBERON:0006603|presumptive mesoderm",enfantParent),"size":"1.0"})
    initialData.append({"uri":ontoLink + "UBERON_0007285","name":"presumptive paraxial mesoderm","children":getchildren("UBERON:0007285|presumptive paraxial mesoderm",enfantParent),"size":"1.0"})
    initialData.append({"uri":ontoLink + "UBERON_0006595","name":"presumptive endoderm","children":getchildren("UBERON:0006595|presumptive endoderm",enfantParent),"size":"1.0"})
    initialData.append({"uri":ontoLink + "UBERON_0006601","name":"presumptive ectoderm","children":getchildren("UBERON:0006601|presumptive ectoderm",enfantParent),"size":"1.0"})
    
    finalDict = {"uri":"","name":"blastula","children":initialData,"size":"1.0"}
        
   
    # Serializing json  
    json_object = json.dumps(finalDict, indent = 4) 
  
    # Writing to sample.json 
    with open(jsonfile, "w") as outfile: 
        outfile.write(json_object) 


if __name__ == '__main__':
    humandev_json()

 
