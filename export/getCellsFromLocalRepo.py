#!/usr/bin/env python

from export.repoConf import *

import sys
import getopt
import requests
import csv

requestURL = HCAOQUERY


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

def getParent(child,n) : 
    print("get parent for " + child)
    parentList = []
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo-term: <http://purl.obolibrary.org/obo/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT distinct ?s ?label {{
    {{ 
    obo-term:{child} rdfs:subClassOf  ?s . }}
    UNION {{
    obo-term:{child} rdfs:subClassOf ?s_axiom .
    ?s_axiom owl:onProperty <http://purl.obolibrary.org/obo/BFO_0000050>  .
    ?s_axiom owl:someValuesFrom ?s . 
    }}
    ?s rdfs:label ?label .
      }}
    """.format(child=child)
    
    myparam = { 'query': query}
    headers = {'Accept' : 'application/sparql-results+json'}
    r=requests.get(requestURL,params=myparam, headers=headers)
    results=r.json()
    
    for row in results["results"]["bindings"] : 
        uri = row["s"]["value"]
        label = row["label"]["value"]
        identifier = uri.split("/")[-1]
        parentList.append(identifier)  
        n= n-1
        if n > 0 : 
            parentL = getParent(identifier,n)
            if len(parentL) >= 1 : 
                parentList.extend(parentL)



        
def askOrgParent(identifier) : 
    if identifier in orgParent.keys() : 
        return orgParent[identifier]
    else : 
        parentList = getParent(identifier,5)
        for parent in parentList : 
            if parent in orgParent.keys() : 
                return orgParent[parent]   
    return ""  


def getCells() : 
    print("get all Cells : contains cells/cyte/blast or has obo namespace CL")
    childrenList = []
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo-term: <http://purl.obolibrary.org/obo/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT distinct ?s ?label {
    ?s rdfs:label ?label .
    ?s <http://www.geneontology.org/formats/oboInOwl#hasOBONamespace> "cell" . 
    FILTER NOT EXISTS { ?s <http://www.geneontology.org/formats/oboInOwl#hasOBONamespace> "cell" . FILTER(regex(str(?s),"CP_")) }
    FILTER NOT EXISTS { ?label <http://www.geneontology.org/formats/oboInOwl#hasOBONamespace> "cell" . FILTER(regex(?label," by ")) }
    }
    """
    
    myparam = { 'query': query}
    headers = {'Accept' : 'application/sparql-results+json'}
    r=requests.get(requestURL,params=myparam, headers=headers)
    results=r.json()
    
    for row in results["results"]["bindings"] : 
        uri = row["s"]["value"]
        label = row["label"]["value"]
        identifier = uri.split("/")[-1]
        
        childrenList.append([identifier,label])
       
    return childrenList



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
   
   
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("                      GET CELLS                                     ")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    cellList = getCells()
    
    print("Get organ child")
    orgParent = {}
    with open("PV/organ_child.csv", "r") as fo:
        csv_reader = csv.reader(fo, delimiter=';')
        print("skipping headers")
        next(csv_reader)
        for lines in csv_reader:
            organ = lines[0]
            print(organ)
            parents = lines[1]
            orgParent[organ] = parents

    
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("FOR EACH CELL, CHECK IF IDENTIFIER IS IN ORGAN CHILD AND CREATE FILE")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    cells = []
    with open("PV/cell_PV.csv", "w") as f:
        f.write('IDENTIFIER,CONCEPT_CODE,SHORT_URI,DEFINITION,DESCRIPTORS,PARENTS,PARENT_IDENTIFIER,value,PUBLIC_ID\n')
    
        for cell in cellList : 
            if cell not in cells : 
                cells.append(cell)
                identifier = cell[0]
                label = cell[1]
                descriptors = ""
                parentStr = askOrgParent(identifier)
                f.write('"getNextPvId(),"","'+identifier+'","","'+descriptors+'","'+parentStr+'","","'+label+'","cell_type"\n')
    