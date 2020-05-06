#!/usr/bin/env python

from export.repoConf import *

import sys
import getopt
import requests
import csv

requestURL = HCAOQUERY

dicoChildParent = {}

def print_usage():
    """Print a help message."""
    print(
        """getListsFromLocalRepo.py [-h][-p] query
This script sends SPARQL query to OBO endpoint http://openstack-192-168-100-40.genouest.org/rdf4j-server/repositories/hcao/
and transforms the result to an openSpecimen 
Arguments:
    -h           Print out this help message.
    -p           Path to the directory for results
"""
    )
    
def getAxiomChildren(broader,withLabel=False) : 
    print("get axiom subclasses that are not part of Organ part")
    childrenList = []

    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo-term: <http://purl.obolibrary.org/obo/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT distinct ?s ?label {{
    ?s rdfs:subClassOf ?s_axiom .
    ?s_axiom owl:onProperty <http://purl.obolibrary.org/obo/BFO_0000050>  .
    ?s_axiom owl:someValuesFrom obo-term:{broader} .  
    ?s rdfs:label ?label .
    #FILTER NOT EXISTS {{?s rdfs:subClassOf* obo-term:UBERON_0000064}}
    #FILTER NOT EXISTS {{?s rdfs:subClassOf* obo-term:CL_0000003}}
    FILTER NOT EXISTS {{ ?s <http://www.geneontology.org/formats/oboInOwl#hasOBONamespace> "cell" }}
    #FILTER NOT EXISTS {{?s rdfs:subClassOf* obo-term:UBERON_0000479}}
    FILTER NOT EXISTS {{?s rdfs:label ?label . FILTER(regex(?label,"cell|blast|cyte|mammalian|adult|right|left","i"))}}
    }}
    """.format(broader=broader)

    #FILTER NOT EXISTS {{?s rdfs:label ?label . FILTER(regex(?label,"cell|blast|cyte|compound organ|system element|region element|segment organ|-derived structure|subdivision of|mammalian|adult|right|left","i"))}}
 
    myparam = { 'query': query}
    headers = {'Accept' : 'application/sparql-results+json'}
    r=requests.get(requestURL,params=myparam, headers=headers)
    results=r.json()

    for row in results["results"]["bindings"] : 
        uri = row["s"]["value"]
        label = row["label"]["value"]
        identifier = uri.split("/")[-1]
        if identifier not in unique.keys() : 
            unique[identifier] = label
            if withLabel :                 
                childrenList.append([identifier,label])
            else : 
                childrenList.append(identifier)     

            childList = getChildren(identifier,withLabel)
            if len(childList) > 1 : 
                childrenList.extend(childList)
       
    return childrenList


def getChildren(broader,withLabel=False) : 
    print("get subclasses that are not part of Organ part and cell and tissue")
    childrenList = []
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo-term: <http://purl.obolibrary.org/obo/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT distinct ?s ?label {{
    ?s rdfs:subClassOf+  obo-term:{broader} . 
    ?s rdfs:label ?label .
    #FILTER NOT EXISTS {{?s rdfs:subClassOf* obo-term:UBERON_0000064}}
    #FILTER NOT EXISTS {{?s rdfs:subClassOf* obo-term:CL_0000003}}
    FILTER NOT EXISTS {{ ?s <http://www.geneontology.org/formats/oboInOwl#hasOBONamespace> "cell" }}
    #FILTER NOT EXISTS {{?s rdfs:subClassOf* obo-term:UBERON_0000479}}
    FILTER NOT EXISTS {{?s rdfs:label ?label . FILTER(regex(?label,"cell|blast|cyte|mammalian|adult|right|left","i"))}}
    }}
    """.format(broader=broader)
    
    #FILTER NOT EXISTS {{?s rdfs:label ?label . FILTER(regex(?label,"cell|blast|cyte|compound organ|system element|region element|segment organ|-derived structure|subdivision of|mammalian|adult|right|left","i"))}}
 
    print(query)
    
    myparam = { 'query': query}
    headers = {'Accept' : 'application/sparql-results+json'}
    r=requests.get(requestURL,params=myparam, headers=headers)
    print(r.status_code)
    results=r.json()
    
    for row in results["results"]["bindings"] : 
        uri = row["s"]["value"]
        label = row["label"]["value"]
        identifier = uri.split("/")[-1]
        if identifier not in unique.keys() : 
            unique[identifier] = label
            if withLabel : 
                childrenList.append([identifier,label])
            else : 
                childrenList.append(identifier)       
        
            axiomChildren = getAxiomChildren(identifier,withLabel)
            if len(axiomChildren) > 1 : 
                childrenList.extend(axiomChildren)
        
    return childrenList

def askParent(identifier) : 
    if identifier in dicoChildParent.keys() : 
        return dico[identifier]
    else :
        return ["HUDECA_0000002"]

if __name__ == "__main__":
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "hr")
    except getopt.error as x:
        print(x)
        sys.exit(0)


    show_help = False
    path = ""
    for opt, arg in optlist:
        if opt == "-h":
            show_help = True
        elif opt == "-r":
            resultPath = arg
        elif opt == "-d":
            sys.stderr.write("The delay parameter is now ignored\n")
    if show_help:
        print_usage()
        sys.exit(0)

    dico = {}
    parentList = []
    
    print("Get main organs and create dico with their children as keys")
    with open("PV/main_organ.csv", "r") as f:
        csv_reader = csv.reader(f, delimiter=',')
        print("skipping headers")
        next(csv_reader)
        for lines in csv_reader:
            print(lines[0])
            if "HUDECA_0000002" not in lines[0] : 
                parentList.append(lines[0])
     
    for elt in parentList : 
        print(elt)
        unique = {}
        listChildren = getChildren(elt)
        dico[elt]= listChildren
        #for child in listChildren : 
            #dicoElt[child] = elt

    
    with open("PV/organ_child.csv", "w") as f2:
        for key,value in dico.items() : 
            for child in value : 
                if child in dicoChildParent.keys() : 
                    myList = dicoChildPArent[child]
                    myList.append(key)
                    dicoChildParent[child] = myList
                else :
                    dicoChildParent[child] = [key]

    
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("Get all organs, find their parents, and create file")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    resultStr = 'IDENTIFIER,CONCEPT_CODE,DEFINITION,PARENT_IDENTIFIER,value\n'
    
    unique = {}
    
    organList = getChildren("UBERON_0000062", True)
    #print("remove duplicates if any")
    #organList = list(dict.fromkeys(organList))
    
    #exceptLabels =  ["compound organ","system element","region element","segment organ","-derived structure","subdivision of","mammalian","adult","right","left"]
 
    
    for organ in organList :        
        identifier = organ[0]
        label = organ[1]
        if identifier not in parentList :
            parentIdList = askParent(identifier)
            for parentId in parentIdList : 
                resultStr+=identifier+"_"+parentId+',"","","'+parentId+'","'+label+'"\n'
    
    
    with open("PV/organs.csv", "w") as f:
        f.write(resultStr)
    