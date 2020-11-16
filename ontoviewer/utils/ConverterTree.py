import json, csv

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
            if "CL:" in child : 
                dict["uri"] = ontoLink + "CL_" + child.split("CL:")[1][-1]
            else : 
                dict["uri"] = "#"
            dict["name"] = child
            childR = getChildren(child,dico)
            if childR != [] : 
                dict["children"] = childR
            dict["size"] = "1.0"
            data.append(dict)
        return data
            
            
        
                

def organ_json():
    csvfile = "../static/cell_by_organ_tree.csv"
    jsonfile = "../static/cell_by_organ_tree.json"
    data = []
    
    with open(csvfile,"r") as csvF :
        csv_reader = csv.reader(csvF, delimiter=';')
        ontoLink = "https://www.ebi.ac.uk/ols/ontologies/cl/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F"
        
        enfantParent = {}
        
        for row in csv_reader:
            for i in range(0,9) : 
                if row[i] == "" : 
                    break
                else : 
                    if row[i] not in enfantParent :
                        if i != 0 : 
                            enfantParent[row[i]] = [row[i-1]]
                        else : 
                            enfantParent[row[i]] = []
                    else : 
                        parents = enfantParent[row[i]].copy()
                        if i!= 0 and row[i-1] not in parents : 
                            parents.append(row[i-1])
                            enfantParent[row[i]] = parents
                            
        print(enfantParent)
        data = []
                        
        for key,value in enfantParent.items() : 
            #si la clé n'est jamais une valeur, on est sur une feuille de dernier niveau
            if enfantParent[key] == [] :
                dict = {}
                if "CL:" in key : 
                    identifier = key.split("CL:")[1]
                    print(identifier)
                    dict["uri"] = ontoLink + "CL_" + key.split("CL:")[1][-1]
                else : 
                    dict["uri"] = "#"
                dict["name"] = key
                dict["children"] = getChildren(key,enfantParent)
                dict["size"] = "1.0"
                data.append(dict)
                
   
    # Serializing json  
    json_object = json.dumps(data, indent = 4) 
  
    # Writing to sample.json 
    with open(jsonfile, "w") as outfile: 
        outfile.write(json_object) 


if __name__ == '__main__':
    organ_json()

 
