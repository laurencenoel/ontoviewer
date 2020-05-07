#!/usr/bin/env python

from export.repoConf import *

import sys
import getopt
import requests
import csv

requestURL = HCAOQUERY

dicoChildParent = {}
listAllTissue = []
listAllOrgPart = []

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
    print("get axiom subclasses")
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
    FILTER NOT EXISTS {{ ?s <http://www.geneontology.org/formats/oboInOwl#hasOBONamespace> "cell" }}
    FILTER NOT EXISTS {{?s rdfs:label ?label . FILTER(regex(?label,"cell|blast|cyte|mammalian|adult|right|left|cistern|space","i"))}}
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
    print("get subclasses")
    childrenList = []
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo-term: <http://purl.obolibrary.org/obo/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT distinct ?s ?label {{
    ?s rdfs:subClassOf*  obo-term:{broader} . 
    ?s rdfs:label ?label .
    FILTER NOT EXISTS {{ ?s <http://www.geneontology.org/formats/oboInOwl#hasOBONamespace> "cell" }}
    FILTER NOT EXISTS {{?s rdfs:label ?label . FILTER(regex(?label,"cell|blast|cyte|mammalian|adult|right|left|cistern|space","i"))}}
    }}
    """.format(broader=broader)
    
    #FILTER NOT EXISTS {{?s rdfs:label ?label . FILTER(regex(?label,"cell|blast|cyte|compound organ|system element|region element|segment organ|-derived structure|subdivision of|mammalian|adult|right|left","i"))}}
 
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

def addToDico(organ,prim) :
    listElt = dico[organ]
    listElt.append(prim)
    dico[organ] = listElt

def askParent(identifier) : 
    if identifier in dicoChildParent.keys() : 
        return dicoChildParent[identifier]
    else :
        return ["HUDECA_0000002"]
        
def askOrganPart(identifier) : 
    for elt in listAllOrgPart : 
        if elt[0] == identifier : 
            return "UBERON_0000064"
    return ""       
      
def askTissue(identifier) : 
    for elt in listAllTissue : 
        if elt[0] == identifier : 
            return "UBERON_0000479 "
    return ""       
            
def checkExceptLabel(label) : 
    exceptLabels =  ["compound organ","system element","region element","segment organ","-derived structure","subdivision of","mammalian","adult","right","left","zone of","regional part of "]
    for elt in exceptLabels : 
        if elt in label : 
            return False
    return True


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
            if "HUDECA_0000002" not in lines[0] : 
                parentList.append(lines[0])
     
    for elt in parentList : 
        unique = {}
        #listChildren = getChildren(elt)
        #listAxiomTop = getAxiomChildren(elt)
        #listAllChildren = listChildren + listAxiomTop
        listAllChildren = getChildren(elt)
        dico[elt]= listAllChildren
        #for child in listChildren : 
            #dicoElt[child] = elt

        
    print("adding primordium and swellings")
    addToDico("UBERON_0000970","UBERON_0003071")
    addToDico("UBERON_0000948","UBERON_0003084")
    addToDico("UBERON_0002046","UBERON_0003091")
    addToDico("UBERON_0005057","UBERON_0005562")
    addToDico("UBERON_0002048","UBERON_0005597")
    addToDico("UBERON_0001264","UBERON_0003921")
    addToDico("UBERON_0000945","UBERON_0012172")
    addToDico("UBERON_0000065","UBERON_0008947")
    addToDico("UBERON_0002107","UBERON_0003894")
    addToDico("UBERON_0002110","UBERON_0006242")
    addToDico("UBERON_0010084","UBERON_0010084")
    addToDico("UBERON_0001723","UBERON_0006260")
    
        
    for organ,value in dico.items() : 
        for child in value : 
            if child in dicoChildParent.keys() : 
                myList = dicoChildParent[child]
                myList.append(organ)
                dicoChildParent[child] = myList
            else :
                dicoChildParent[child] = [organ]
                    
    with open("PV/organ_child.csv", "w") as f2:
        for child,parentList in dicoChildParent.items() : 
            for parent in parentList : 
                f2.write(child+";"+parent+"\n")
                
                
    print("Get organ parts")
    unique = {}
    #listChildOrgPart = getChildren("UBERON_0000064",True)
    #listAxiomTopOrgPart = getAxiomChildren("UBERON_0000064",True)
    #listAllOrgPart = listChildOrgPart + listAxiomTopOrgPart
    
    listAllOrgPart = getChildren("UBERON_0000064",True)

    with open("PV/organ_part.csv", "w") as f3:
        for organ_part in listAllOrgPart :
            identifier = organ_part[0]
            label = organ_part[1]
            f3.write(identifier+";"+label+"\n")   
    
    print("Get Tissue")
    unique = {}
    #listChildTissue = getChildren("UBERON_0000479",True)
    #listAxiomTopTissue = getAxiomChildren("UBERON_0000479",True)
    #listAllTissue = listChildTissue + listAxiomTopTissue
    listAllTissue = getChildren("UBERON_0000479",True)
    
    
    with open("PV/tissue.csv", "w") as f4:
        for tissue in listAllTissue :
            identifier = tissue[0]
            label = tissue[1]
            f4.write(identifier+";"+label+"\n") 

    
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("Get all organs, find their parents, and create file")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    resultStr = 'IDENTIFIER,CONCEPT_CODE,SHORT_URI,DEFINITION,DESCRIPTORS,PARENTS,PARENT_IDENTIFIER,value,PUBLIC_ID\n'
    
    unique = {}
    
    organList = getChildren("UBERON_0000062", True)
    #print("remove duplicates if any")
    #organList = list(dict.fromkeys(organList))
    
  
    
    for organ in organList :        
        identifier = organ[0]
        label = organ[1]

        if identifier not in parentList and "CL_" not in identifier :
            isNotException = checkExceptLabel(label)
            if isNotException : 
                descriptors = ""
                descriptors = askOrganPart(identifier)
                #descriptors += askTissue(identifier)
                if askTissue == "" : 
                    parentIdList = askParent(identifier)
                    parentStr = " ".join(parentIdList)
                    resultStr+='"getNextPvId(),"","'+identifier+'","","'+descriptors+'","'+parentStr+'","","'+label+'","organ"\n'
    
    print("add bone marrow")
    resulStr+='"getNextPvId(),"","UBERON_0002371","","UBERON_0000479","UBERON_0004765","","Bone marrow","organ"\n'
    
    with open("PV/organs.csv", "w") as f:
        f.write(resultStr)
    