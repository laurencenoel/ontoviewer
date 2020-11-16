import json, csv

def organ_json():
    csvfile = "../static/cell_by_organ_table.csv"
    jsonfile = "../static/cell_by_organ_table.json"
    data = []
    
    with open(csvfile,"r") as csvF :
        csv_reader = csv.reader(csvF, delimiter=';')
        line_count = 0
        ontoLink = "https://www.ebi.ac.uk/ols/ontologies/cl/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F"
       
        for row in csv_reader:
            dict={}
            dict["organ"]=row[0]
            dict["cell_name"]=row[1]
            id = row[2].replace("_",":")
            dict["onto_ID"] = "<a href='"+ontoLink+row[2]+"' target='_blank'>"+id+"</a>"
            data.append(dict)
    
    # Serializing json  
    json_object = json.dumps(data, indent = 4) 
  
    # Writing to sample.json 
    with open(jsonfile, "w") as outfile: 
        outfile.write(json_object) 


if __name__ == '__main__':
    organ_json()

 
