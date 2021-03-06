#!/usr/bin/env python

# -*- coding: utf-8 -*-


# Module metadata variables
__author__ = "Rafael Barrero Rodriguez"
__credits__ = ["Rafael Barrero Rodriguez", "Jose Rodriguez", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__email__ = "rbarreror@cnic.es"
__status__ = "Development"


# Import modules
import sys
import os
import csv
import traceback
import requests
import pandas as pd
from tqdm import tqdm

import pdb

# Local functions
def tsvReader(fileName):
    """
    Input:
        - fileName: String containing name of table.tsv
    Output:
        - rowList: List of lists containing [[name1, id1], [name2, id2]...]
    """

    with open(fileName, 'r', encoding="utf-8") as f:
        rowList = [] # List of lists containing [[name1, id1], [name2, id2]...]
        tsvFile = csv.reader(f, delimiter="\t")
        next(tsvFile)

        for row in tsvFile:
            rowList.append(row[:2])
        
    return rowList


def getSynonym(name):
    """
    Input:
        - name: String containin the name of a compound
    Output:
        - synonymsList: List of strings with retrieved synonyms. If error, None is returned
    """

    url_prolog = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    url_input = "/compound/name/" + name
    operation = "/synonyms"
    output = "/TXT"

    url = url_prolog + url_input + operation + output

    try:
        response = requests.get(url)
    
    except:
        traceback.print_exc()
        return None

    if response.ok:
        synonymsList = response.text.split('\n')
        return synonymsList[:-1]
    
    else: 
        return None



def getAllSynonyms(compoundList):
    """
    Input:
        - compoundList: List of lists containing [[name1, id1], [name2, id2]...]
    Output:
        - allSynonyms: List of lists containing [[name1, id1], [name2, id2]...]
    """

    reviewed_ID = []
    retrievedSynonyms = []

    for name, db_id in tqdm(compoundList):
        
        if db_id in reviewed_ID:
            continue
        
        req = getSynonym(name)
        
        if req:
            reviewed_ID.append(db_id)
            retrievedSynonyms.append([req, db_id])
    
    allSynonyms = [[name, db_id] for syns_list, db_id in retrievedSynonyms for name in syns_list] + compoundList
    
    return allSynonyms



# Main function
def main():
    """
    main function
    """

    fileName = sys.argv[1]

    scriptDir = os.path.dirname(os.path.realpath(__file__))

    # Get list of lists with [[name1, id1], [name2, id2]...]
    compoundList = tsvReader(fileName)

    # Get all synonyms
    allSynonyms = getAllSynonyms(compoundList)

    # Write table.tsv
    df = pd.DataFrame(allSynonyms, columns=['Name', 'ID'])
    df.drop_duplicates(inplace=True)
    df.to_csv(os.path.join(scriptDir,"allSynonyms.tsv"), sep='\t', index=False)


if __name__ == "__main__":

    main()