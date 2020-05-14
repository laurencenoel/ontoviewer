from rdflib import URIRef, Literal,Graph
from SPARQLWrapper import SPARQLWrapper,N3,JSON
import requests
from rdflib.plugins.stores import sparqlstore
from rdflib.namespace import SKOS,RDF,RDFS,OWL,DC,XSD
import json
from conf.repo import *

class Entry(object) :

    def __init__(self,identifier,uriBase,queryEndpoint,updateEndpoint):
        self._id = identifier
        self._stUri = uriBase + self._id
        self._uri = URIRef(self._stUri)
        self._stUriBase = uriBase
        self._queryEndpoint = queryEndpoint
        self._updateEndpoint = updateEndpoint

    def get_stUriBase(self):
        return self._stUriBase

    def _set_stUriBase(self,value):
        self._stUriBase = value

    uriBase = property(get_stUriBase, doc="Entry UriBase")

    def get_queryEndpoint(self):
        return self._queryEndpoint

    def _set_queryEndpoint(self,value):
        self._queryEndpoint = value
        
    queryEndpoint = property(get_queryEndpoint, doc="Entry queryEndpoint")

    def get_updateEndpoint(self):
        return self._updateEndpoint

    def _set_updateEndpoint(self,value):
        self._updateEndpoint = value
        
    updateEndpoint = property(get_updateEndpoint, doc="Entry updateEndpoint")


    def get_id(self):
        return self._id

    def _set_id(self,value):
        self._id = value
        self._set_stUri(self.get_stUriBase+self._id)

    id = property(get_id, doc="Entry identifier")


    def get_stUri(self):
        return self._stUri

    def _set_stUri(self,value):
        self._stUri = value
        self._set_uri(self._stUri)

    stUri = property(get_stUri, doc="Entry string uri")

    def get_uri(self):
        return self._uri

    def _set_uri(self,value):
        self._uri = URIRef(value)

    uri = property(get_uri, doc="Entry Uri")


    def getEntityGraph(self) :
        #print("get entity graph " + self._uri + " with : " + self._stUriBase)
        sparql = SPARQLWrapper(self._queryEndpoint)
        queryDesc = "DESCRIBE <{s}>".format(s=self._stUri)
        queryMore = "CONSTRUCT {{ ?s2 ?p2 ?o2 }} WHERE {{ <{s}> ?p  ?s2 . ?s2 ?p2 ?o2 }}".format(s=self._stUri)
        sparql.setQuery(queryDesc)
        sparql.setReturnFormat(N3)
        results = sparql.query().convert()
        sparql.setQuery(queryMore)
        rg = Graph()
        try : 
            results2 = sparql.query().convert()
        except : 
            print("The graph was not retrieved")
        else : 
            rg.parse(data=results, format="n3")
            rg.parse(data=results2, format="n3")
        finally : 
            return rg


    def getDescribeGraph(self) :
        #print("get entity graph " + self._uri + " with : " + self._stUriBase)
        sparql = SPARQLWrapper(self._queryEndpoint)
        queryDesc = "DESCRIBE <{s}>".format(s=self._stUri)
        sparql.setQuery(queryDesc)
        sparql.setReturnFormat(N3)
        results = sparql.query().convert()
        rg = Graph()
        rg.parse(data=results, format="n3")
        return rg


    def getIdentityGraph(self) :
        #print("get entity graph " + self._uri + " with : " + self._stUriBase)
        sparql = SPARQLWrapper(self._queryEndpoint)
        query = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  PREFIX model: <http://purl.amypdb.org/model/> CONSTRUCT {{ <{s}> rdfs:label ?label . <{s}> model:accession ?accession }} WHERE {{ <{s}> rdfs:label ?label . <{s}> model:accession ?accession }}".format(s=self._stUri)
        sparql.setQuery(query)
        sparql.setReturnFormat(N3)
        results = sparql.query().convert()
        rg = Graph()
        rg.parse(data=results, format="n3")
        return rg
        
    def getLabel(self) :
        #print("get entity graph " + self._uri + " with : " + self._stUriBase)
        sparql = SPARQLWrapper(self._queryEndpoint)
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX model: <http://purl.amypdb.org/model/>
        PREFIX base: <{base}>
        SELECT ?label WHERE {{ base:{ide} rdfs:label ?label . }}""".format(ide=self._id,base=self._stUriBase)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results=sparql.query().convert()
        label = ""
        for row in results["results"]["bindings"] :
            label = row["label"]["value"] 
        return label


    def exists(self,linkedRef=None) :
        ref = ""
        if linkedRef != None :
            ref=str(linkedRef)            
        else : 
            ref=self._stUri
        query= " ASK {{ <{uri}> ?p ?o }} ".format(uri=ref)     
        headers = {'content-type' : 'application/x-www-form-urlencoded'}
        myparam = { 'query': query }
        try : 
            r=requests.get(self._queryEndpoint,myparam,headers=headers)
        except :
            print("There was a problem trying to check the existence of  "  + ref)
            return False
        else : 
            exists = r.json()['boolean']
            return exists



    def existsLiteral(self,label) :
        ref=self._stUri
        query= " ASK {{ <{uri}> ?p  '{label}' }} ".format(uri=ref,label=label)     
        headers = {'content-type' : 'application/x-www-form-urlencoded'}
        myparam = { 'query': query }
        try : 
            r=requests.get(self._queryEndpoint,myparam,headers=headers)
        except :
            print("There was a problem trying to check the existence of  "  + label)
            return False
        else : 
            exists = r.json()['boolean']
            return exists

    def existsAccess(self) :
        ref=self._stUri
        query= "PREFIX model: <http://purl.amypdb.org/model/>  ASK {{ <{uri}> model:accession  ?acc }} ".format(uri=ref)     
        headers = {'content-type' : 'application/x-www-form-urlencoded'}
        myparam = { 'query': query }
        try : 
            r=requests.get(self._queryEndpoint,myparam,headers=headers)
        except :
            print("There was a problem trying to check the existence of  "  + label)
            return False
        else : 
            exists = r.json()['boolean']
            return exists

    def addEntityGraphToStore(self,graph) :
        query = " INSERT DATA {{ GRAPH <{g}> {{ {gr} }} }} ".format(gr=graph.serialize(format='nt').decode(),g=self._stUriBase)
        headers = {'content-type' : 'application/x-www-form-urlencoded'}
        cont = URIRef(self._stUriBase)
        myparam = { 'context' : cont,'update': query}
        try : 
            r=requests.post(self._updateEndpoint,myparam,headers=headers) 
        except :
            print("There was a problem trying to add  "  + self._stUri + " to the triple store")


class HcaoEntry(Entry) :

    def __init__(self,identifier):
        super().__init__(identifier,STR_HCAO,HCAOQUERY,HCAOUPDATE)

 



class Protein(KbEntry):    



    def __init__(self,identifier):
        super().__init__(identifier)
        self._type = AMMODEL.Protein
     
    def get_type(self):
        return self._type

    type = property(get_type,doc="Entry Type")

    def getPublications(self) :
        uniId = STR_UNIKB + self._id
        query="PREFIX unicore:<http://purl.uniprot.org/core/> \
        PREFIX owl: <http://www.w3.org/2002/07/owl#> \
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#> \
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
        PREFIX foaf: <http://xmlns.com/foaf/0.1/> \
        SELECT ?title ?date ?name ?volume ?pages ?pubmed \
        (GROUP_CONCAT(DISTINCT ?author; SEPARATOR=', ') AS ?authors) \
        FROM <http://purl.uniprot.org/uniprot/> \
        WHERE {{ \
        <{prot}> unicore:citation ?citation . \
        ?citation unicore:author ?author . \
        ?citation unicore:title ?title . \
        ?citation unicore:date ?date . \
        ?citation unicore:name ?name . \
        ?citation foaf:primaryTopicOf ?pubmed . \
        OPTIONAL {{?citation unicore:volume ?volume . ?citation unicore:pages ?pages . }} \
        }} GROUP BY ?title ?date ?name ?volume ?pages ?pubmed ORDER BY DESC(?date) LIMIT 30 ".format(prot=uniId)

        sparql = SPARQLWrapper(UNIQUERY)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results=sparql.query().convert()
        data = []
        for row in results["results"]["bindings"] :
            dict =  {}
            for elt in results["head"]["vars"] : 
                if elt in row :
                    dict[elt] = row[elt]["value"] 
                else : 
                    dict[elt] = ""
            data.append(dict)

        return data
