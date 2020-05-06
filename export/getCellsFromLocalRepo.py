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
    }
    """
    
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
   
    cellList = getCells()
    
    resultStr = 'IDENTIFIER,CONCEPT_CODE,DEFINITION,value,PUBLIC_ID\n'
     
    for cell in cellList :
        identifier = organ[0]
        label = organ[1]
        resultStr+=identifier+',"","","'+label+'","cells"\n'
    
    
    with open("PV/cells.csv", "w") as f:
        f.write(resultStr)
    