#!/usr/bin/env python

from export.repoConf import *

import sys
import getopt
import requests
import csv

requestURL = HCAOQUERY

if __name__ == "__main__":
   
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("                    CHECK DUPLICATE                                 ")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    files = ["PV/organs_PV.csv","PV/tissue_PV.csv","PV/cell_PV.csv"]
    for file in files : 
        with open(file, "r") as f:
            unique=[]
            csv_reader = csv.reader(f, delimiter=',')
            for lines in csv_reader:
                short_uri = lines[2]
                if short_uri in unique :
                    print(file + " " + short_uri + " ".join(lines))
                else :
                    unique.append(short_uri)
    
