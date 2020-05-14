#!/usr/bin/env python

from conf.repo import *

import sys
import getopt
import requests
import csv
import json


requestURL = HCAOQUERY

dicoChildParent = {}
dicoOriginParent = {}
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
    
def getChildrenOrAxiom(broader,withLabel=False) : 
    print("get subclasses for " + broader)
    childrenList = []
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo-term: <http://purl.obolibrary.org/obo/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT distinct ?s ?label {{
    {{
    ?s rdfs:subClassOf  obo-term:{broader} . }}
    UNION {{
    ?s rdfs:subClassOf ?s_axiom .
    ?s_axiom owl:onProperty <http://purl.obolibrary.org/obo/BFO_0000050>  .
    ?s_axiom owl:someValuesFrom obo-term:{broader} . }}
    ?s rdfs:label ?label .
    #FILTER NOT EXISTS {{ ?s <http://www.geneontology.org/formats/oboInOwl#hasOBONamespace> "cell" }}
    #FILTER NOT EXISTS {{?s rdfs:label ?label . FILTER(regex(?label,"cell|blast|cyte|mammalian|adult|right|left|cistern|space","i"))}}
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
        
            childL = getChildrenOrAxiom(identifier,withLabel)
            if len(childL) >= 1 : 
                childrenList.extend(childL)
        
    return childrenList

def getLabels(idList) : 
    
    labels = ""
    for identifier in idList : 

        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX obo-term: <http://purl.obolibrary.org/obo/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT distinct ?label {{
        obo-term:{ide} rdfs:label ?label .
        }}
        """.format(ide=identifier)
        
        myparam = { 'query': query}
        headers = {'Accept' : 'application/sparql-results+json'}
        r=requests.get(requestURL,params=myparam, headers=headers)
        results=r.json()
    
        for row in results["results"]["bindings"] : 
            label = row["label"]["value"]
            labels += label + ", "
            
    if len(labels) > 2 :
        labels = labels[:-2]
        
    return labels



def getOrigin(organ) : 
    print("get Origin for " + organ)
    childrenList = []
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo-term: <http://purl.obolibrary.org/obo/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT distinct ?s ?label {{
    {{  obo-term:{organ} <http://purl.obolibrary.org/obo/RO_0002202>|<http://purl.obolibrary.org/obo/RO_0002494> ?s . }}
    UNION {{
    obo-term:{organ} rdfs:subClassOf ?s_axiom .
     {{ ?s_axiom owl:onProperty <http://purl.obolibrary.org/obo/RO_0002202>  . }} 
    UNION {{ ?s_axiom owl:onProperty <http://purl.obolibrary.org/obo/RO_0002494> . }}
    ?s_axiom owl:someValuesFrom ?s . }}
    ?s rdfs:label ?label .
    }}
    """.format(organ=organ)
    
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
            childrenList.append(identifier)       
            childL = getOrigin(identifier)
            if len(childL) >= 1 : 
                childrenList.extend(childL)
        
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
        
def askSystem(identifier) : 
    if identifier in dicoChildSyst.keys() : 
        return dicoChildSyst[identifier]
    return ["HUDECA_0000002"]
        
def askOrganPart(identifier) : 
    for elt in listAllOrgPart : 
        if elt[0] == identifier : 
            return "UBERON_0000064"
    return ""       
      
def askTissue(identifier) : 
    for elt in listAllTissue : 
        if elt[0] == identifier : 
            return "UBERON_0000479"
    return ""     

      
            
def askCell(identifier) : 
    for elt in listAllCells : 
        if elt[0] == identifier : 
            return "CL_0000003"
    return ""       
                        

def checkExceptLabel(label) : 
    exceptLabels =  ["compound organ","system element","region element","segment organ","-derived structure","subdivision of","mammalian","adult","right","left","zone of","regional part of ","cistern","space"]
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
    dicoOrigin = {}
    
    print("Get main organs and create dico with their children as keys")
    with open("PV/main-organ.csv", "r") as f:
        csv_reader = csv.reader(f, delimiter=',')
        print("skipping headers")
        next(csv_reader)
        for lines in csv_reader:
            if "HUDECA_" not in lines[2] : 
                parentList.append(lines[2])
     
    for elt in parentList : 
        unique = {}
        listAllChildren = getChildrenOrAxiom(elt)
        dico[elt]= listAllChildren
        #to have the element as its own parent
        addToDico(elt,elt)
        
        unique = {}
        listAllOrigin = getOrigin(elt)
        dicoOrigin[elt] = listAllOrigin

        
    print("create file for organs with their children as keys")
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
            parentStr = " ".join(parentList)
            f2.write(child+";"+parentStr+"\n")
            
            
    print("create file for origins with their origin as keys")
    for organ,value in dicoOrigin.items() : 
        for child in value : 
            if child in dicoOriginParent.keys() : 
                myList = dicoOriginParent[child]
                myList.append(organ)
                dicoOriginParent[child] = myList
            else :
                dicoOriginParent[child] = [organ]
                    
    with open("PV/origin_parent.csv", "w") as forigin:
        for child,parentList in dicoOriginParent.items() : 
            parentStr = " ".join(parentList)
            forigin.write(child+";"+parentStr+"\n")
    
    
                
    print("Get organ parts")
    unique = {}
    #listChildOrgPart = getChildren("UBERON_0000064",True)
    #listAxiomTopOrgPart = getAxiomChildren("UBERON_0000064",True)
    #listAllOrgPart = listChildOrgPart + listAxiomTopOrgPart
    
    listAllOrgPart = getChildrenOrAxiom("UBERON_0000064",True)

    with open("PV/organ_part_labels.csv", "w") as f3:
        for organ_part in listAllOrgPart :
            identifier = organ_part[0]
            label = organ_part[1]
            f3.write(identifier+";"+label+"\n")   
    
    print("Get Tissue")
    unique = {}
    #listChildTissue = getChildren("UBERON_0000479",True)
    #listAxiomTopTissue = getAxiomChildren("UBERON_0000479",True)
    #listAllTissue = listChildTissue + listAxiomTopTissue
    listAllTissue = getChildrenOrAxiom("UBERON_0000479",True)
     
    with open("PV/tissue_labels.csv", "w") as ftissue:
        for tissue in listAllTissue :
            identifier = tissue[0]
            label = tissue[1]
            ftissue.write(identifier+";"+label+"\n") 
  
    print("Get Cells")
    unique = {}
    listAllCells = getChildrenOrAxiom("CL_0000003",True)  
    
    with open("PV/cells_labels.csv", "w") as fcells:
        for cell in listAllCells :
            identifier = cell[0]
            label = cell[1]
            fcells.write(identifier+";"+label+"\n") 

    
    systList = []
    print("Get anatomic_system")
    with open("PV/anatomic-system.csv", "r") as f:
        csv_reader = csv.reader(f, delimiter=',')
        print("skipping headers")
        next(csv_reader)
        for lines in csv_reader:
            systList.append(lines[0])
    dicoSyst={}
    for elt in systList : 
        unique = {}
        listAllSyst = getChildrenOrAxiom(elt)
        dicoSyst[elt]= listAllSyst
        
    dicoChildSyst = {}
    print("create file for systems with their children as keys")
    for syst,value in dicoSyst.items() : 
        for child in value : 
            if child in dicoChildSyst.keys() : 
                myList = dicoChildSyst[child]
                myList.append(syst)
                dicoChildSyst[child] = myList
            else :
                dicoChildSyst[child] = [syst]
                    
    with open("PV/system-child.csv", "w") as fsyst:
        for child,parentList in dicoChildSyst.items() : 
            parentStr = " ".join(parentList)
            fsyst.write(child+";"+parentStr+"\n")

    
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("Get all organs, find their parents, and create file")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    unique = {}
    organList = getChildrenOrAxiom("UBERON_0000062", True)
    
    with open("PV/organ-PV.csv", "w") as f:
    
        f.write("IDENTIFIER,CONCEPT_CODE,SHORT_URI,DEFINITION,DESCRIPTORS,PARENTS,value,PUBLIC_ID\n")
    
        for organ in organList :        
            identifier = organ[0]
            label = organ[1]

            if identifier not in parentList :
                isNotException = checkExceptLabel(label)
                if isNotException : 
                    descriptors = ""
                    descriptors = askOrganPart(identifier)
                    #descriptors += askTissue(identifier)
                    if askTissue(identifier) == "" and askCell(identifier) == "" : 
                        parentIdList = askParent(identifier)
                        parentStr = " ".join(parentIdList)
                        f.write('"getNextPvId()","","'+identifier+'","","'+descriptors+'","'+parentStr+'","'+label+'","organ_type"\n')
    
        print("add bone marrow")
        f.write('"getNextPvId()","","UBERON_0002371","","UBERON_0000479","UBERON_0004765","Bone marrow","organ_type"\n')
    
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("Create json file with main organs, organ part, type, system ")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    datajson = []
    for organ in organList : 
        identifier = organ[0]
        label = organ[1]
        isNotException = checkExceptLabel(label)
            if isNotException : 
                if askTissue(identifier) == "" and askCell(identifier) == "" : 
                    mainOrganIdList = askParent(identifier)
                    organList = getLabels(mainOrganIdList)
                    systemIdList = askSystem(identifier)
                    systemList = getLabels(systemIdList)
                    descriptors = askOrganPart(identifier)
                    if descriptors == "" : 
                        descriptors = "subClass"
                    else : 
                        descriptors = "specific organ part"
                    if organList != label :
                        datajson.append({"organ":organList,"organ_type":label,"type":descriptors,"anatomic_system":systemList})
    
    with open("../ontoviewer/static/organ.json", "w") as outfile:
        json.dump(datajson, outfile)
    


    