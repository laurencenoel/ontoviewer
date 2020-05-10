#!/usr/bin/env python

from export.repoConf import *

import sys
import getopt
import requests
import csv

requestURL = MONDOQUERY

      
def getChildrenOrAxiom(broader,withLabel=False) : 
    print("get subclasses for " + broader)
    childrenList = []
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX obo-term: <http://purl.obolibrary.org/obo/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT distinct ?s ?label  {{
    {{ 
    ?s rdfs:subClassOf  obo-term:{broader} . }}
    UNION {{
    ?s rdfs:subClassOf ?s_axiom .
    ?s_axiom owl:onProperty <http://purl.obolibrary.org/obo/BFO_0000050>  .
    ?s_axiom owl:someValuesFrom obo-term:{broader} . 
    }}
    ?s rdfs:label ?label .
    }}
    """.format(broader=broader)
    
 
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
	
def checkGeneticDisorder(identifier) : 
    if identifier in gDisorderList : 
        return True
    return False   


if __name__ == "__main__":
   
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("          GET INFERTILITY DISORDERS                                 ")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    
    unique={}
    gDisorderList = getChildrenOrAxiom("MONDO_0017143")
    
    unique={}
    fDisorderList = getChildrenOrAxiom("MONDO_0021124",True)
    
    unique={}
    mDisorderList = getChildrenOrAxiom("MONDO_0005372",True)
    
    
    
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("               GET FEMALE INFERTILITY  DISORDERS                    ")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    unique = []
    with open("PV/f-infertility-disorder.csv", "w") as f:
        f.write('IDENTIFIER,CONCEPT_CODE,SHORT_URI,DEFINITION,value,PUBLIC_ID\n')
    
        for disorder in fDisorderList : 
            if disorder not in unique : 
                unique.append(disorder)
                identifier = disorder[0]
                label = disorder[1]
                isGenetic = checkGeneticDisorder(identifier)
                if isGenetic == False : 
                    f.write('"getNextPvId()","","'+identifier+'","","'+label+'","f_infertility_disorder"\n')
    
            
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("               GET MALE INFERTILITY  DISORDERS                      ")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    unique = []
    with open("PV/m-infertility-disorder.csv", "w") as f:
        f.write('IDENTIFIER,CONCEPT_CODE,SHORT_URI,DEFINITION,value,PUBLIC_ID\n')
    
        for disorder in mDisorderList : 
            if disorder not in unique : 
                unique.append(disorder)
                identifier = disorder[0]
                label = disorder[1]
                isGenetic = checkGeneticDisorder(identifier)
                if isGenetic == False : 
                    f.write('"getNextPvId()","","'+identifier+'","","'+label+'","m_infertility_disorder"\n')