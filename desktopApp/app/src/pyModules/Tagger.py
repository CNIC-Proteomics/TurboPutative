#!/usr/bin/env python

# -*- coding: utf-8 -*-


# Module metadata variables
__author__ = "Rafael Barrero Rodriguez"
__credits__ = ["Rafael Barrero Rodriguez", "Jose Rodriguez", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "0.0.1"
__maintainer__ = "Jose Rodriguez"
__email__ = "rbarreror@cnic.es;jmrodriguezc@cnic.es"
__status__ = "Development"


# Import modules 
import os
import sys
import argparse
import configparser
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import re
import multiprocessing
from multiprocessing import Pool, cpu_count

import pdb


###################
# Local functions #
###################

class NoNameColumn(Exception):
    pass

def openFile(infile, row):
    '''
    '''

    extension = os.path.splitext(infile)[1]

    if extension == '.xls':
        df = pd.read_excel(infile, header=row, engine="xlrd")

    elif extension == '.xlsx':
        df = pd.read_excel(infile, header=row, engine="openpyxl")

    else: 
        logging.info(f"ERROR: Cannot read file with {extension} extension")
        sys.exit(52)


    return df

def readInfile(infile, row):
    '''
    Input:
        - infile: Path where the file is located
        - row: Index (0-based) of column headers, where the table starts
    Output:
        - df: Pandas dataframe with the table
    '''

    infile_base_name = re.escape(os.path.splitext(os.path.basename(infile))[0])
    file = [file for file in os.listdir(os.path.dirname(infile)) if re.search(f'^{infile_base_name}\.(?!.*\.)', file)][0]
    
    infile = os.path.join(os.path.dirname(infile), file)

    log_str = f'Reading input file: {str(Path(infile))}'
    logging.info(log_str)

    try:
        df = openFile(infile, row)
        
        while ("Name" not in df.columns) and (row+1 < 2):
            row += 1
            df = openFile(infile, row)
        
        if "Name" not in df.columns:
            raise NoNameColumn("ERROR: 'Name' column was not found")

        # Make sure that all column names are string
        df.rename(columns={name: str(name) for name in df.columns}, inplace=True)
    
    except NoNameColumn:
        log_str = f'Error when reading {str(Path(infile))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'NoNameColumn: {value}'
        logging.info(log_str)
    
        sys.exit(11) # Status code for column name error
    
    except:
        log_str = f'Error when reading {str(Path(infile))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'{exctype}: {value}'
        logging.info(log_str)

        sys.exit(10) # Status code for file format
    
    log_str = f'{str(Path(infile))} was read'
    logging.info(log_str)

    return df


def getFirstSynonym(compound):
    '''
    Input:
        - compound: string containing compound name (may have synonyms)
    Output:
        - string with the first synonym (separator: ;\n or \n) to lower case
    '''
    return re.split(r'(;\n|\n)', compound)[0].strip().lower()


def readFoodTable(path):
    '''
    Input:
        - path: String containing the path with the food containing table
    
    Output:
        - food_list: Numpy array of strings containing all food compounds in the table
    '''

    logging.info(f"Reading Food Table: {path}")

    df = pd.read_csv(path, header=0, sep="\t", dtype=str)
    food_list = np.array(df.iloc[:, 0].drop_duplicates(keep='first', inplace=False))

    return food_list


def getNameColumnIndex(column_names):
    '''
    Input:
        - column_names: Pandas series containing the names of the columns in the infile table
    
    Output:
        - An integer indicating the position of the Name column
    '''

    return int(np.where(column_names == "Name")[0][0])


def foodTaggerBatch(df, food_list):
    '''
    Input:
        - df: Pandas dataframe containing batch of the total content
        - food_list: String Numpy Array with all food compounds extracted from the database
    
    Output:
        - df: Pandas dataframe with the "Food" tag added in a new column
    '''

    # Get numpy array with compound names in the dataframe
    compound_names = np.array(df.loc[:, 'Name']) 

    # Tag corresponding compounds using food list
    food_tag_from_db = ["" if pd.isna(compound) else "Food" if getFirstSynonym(compound) in food_list else "" for compound in compound_names]

    # Tag compounds that fits regular expression
    food_tag_from_regex = ["" if pd.isna(compound) else "Food" if re.search(r'(?i)^ent-', compound) else "" for compound in compound_names]

    # Combine Food tags
    food_tag = ["Food" if "Food" in tag else "" for tag in zip(food_tag_from_db, food_tag_from_regex)]

    # Add Food tag column to the dataframe
    name_column_index = getNameColumnIndex(df.columns)
    df.insert(name_column_index+1, "Food", food_tag, True)
    
    return df


def foodTagger(df, n_cores):
    '''
    Input:
        - df: Pandas dataframe containing the whole content
        - n_cores: Integer indicating the number of cores used in the multiprocessing
    
    Output:
        - df_out: Pandas dataframe with the whole content and the added tag
    '''
    
    logging.info("Start food tagging")
    
    # Get numpy array with food compounds in database
    food_list = readFoodTable(args.foodList)

    # Tagging without parallel processes (AVOID MEMORY ERROR)
    # df_out = foodTaggerBatch(df, food_list)

    # Split dataframe so that each batch is processed by one core
    df_split = np.array_split(df, n_cores)
        
    # Create list of tuples. Each tuple contains arguments received by foodTaggerBatch in each subprocess
    subprocess_args = [(df_i, food_list) for df_i in df_split]
        
    with Pool(n_cores) as p:

        logging.info("Tagging food compounds")
        result = p.starmap(foodTaggerBatch, subprocess_args)
        df_out = pd.concat(result)
    
    logging.info("Finished food tagging")

    return df_out


def readDrugTable(path):
    '''
    Input:
        - path: String containing the path to the Drug database
    
    Output:
        - drug_list: String Numpy Array containing drugs name extracted from the database
    '''

    logging.info(f"Reading Drug Table: {path}")

    # Import drug table as a pandas dataframe
    df = pd.read_csv(path, header=0, sep="\t", dtype=str)

    # Extract drug list name from df as a numpy array
    drug_list = np.array(df.iloc[:, 0])

    return drug_list


def drugTaggerBatch(df, drug_list):
    '''
    Input:
        - df: Pandas dataframe containing a batch of the whole infile dataframe
        - drug_list: String Numpy Array containing all drug compounds in the database
    
    Output:
        - df: Pandas dataframe with the drug tag added in a new column
    '''

    # Get numpy array with compound in input table
    compound_names = np.array(df.loc[:, 'Name']) 

    # Tag corresponding compounds
    drug_tag = ["" if pd.isna(compound) else "Drug" if getFirstSynonym(compound) in drug_list else "" for compound in compound_names]

    # Add Drug tag column to the dataframe
    name_column_index = getNameColumnIndex(df.columns)
    df.insert(name_column_index+1, "Drug", drug_tag, True)
    
    return df


def drugTagger(df, n_cores):
    '''
    Input:
        - df: Pandas dataframe containing the whole infile content
        - n_cores: Integer indicating the number of cores used in the multiprocessing

    Output: df_out: Pandas dataframe containing the whole infile content with the Drug Tag 
    added in a new column
    '''

    logging.info("Start drug tagging")

    # Get numpy array with drug list
    drug_list = readDrugTable(args.drugList)

    # Tagging without parallel process (AVOID MEMORY ERROR)
    # df_out = drugTaggerBatch(df, drug_list)

    # Split dataframe so that each batch is processed by one core
    df_split = np.array_split(df, n_cores)

    # Create list with parameters received by each drugTaggerBatch function in each subprocess
    subprocess_args = [(df_i, drug_list) for df_i in df_split]

    with Pool(n_cores) as p:

        logging.info("Tagging drug compounds")
        result = p.starmap(drugTaggerBatch, subprocess_args)
        df_out = pd.concat(result)
    
    logging.info("Finished drug tagging")

    return df_out

def readMicrobialTable(path):
    '''
    Input:
        - path: String containing the path to the microbial database
    
    Output:
        - microbial_list: String Numpy Array containing micrbial name extracted from the database
    '''

    logging.info(f"Reading Microbial Table: {path}")

    # Import drug table as a pandas dataframe
    df = pd.read_csv(path, header=0, sep="\t", dtype=str)

    # Extract drug list name from df as a numpy array
    microbial_list = np.array(df.iloc[:, 0])

    return microbial_list


def microbialTaggerBatch(df, microbial_list):
    '''
    Input:
        - df: Pandas dataframe containing a batch of the whole infile dataframe
        - microbial_list: String Numpy Array containing all microbial compounds in the database
    
    Output:
        - df: Pandas dataframe with the microbial tag added in a new column
    '''

    # Get numpy array with compound in input table
    compound_names = np.array(df.loc[:, 'Name']) 

    # Tag corresponding compounds
    microbial_tag = ["" if pd.isna(compound) else "MC" if getFirstSynonym(compound) in microbial_list else "" for compound in compound_names]

    # Add Drug tag column to the dataframe
    name_column_index = getNameColumnIndex(df.columns)
    df.insert(name_column_index+1, "Microbial", microbial_tag, True)
    
    return df


def microbialTagger(df, n_cores):
    '''
    Input:
        - df: Pandas dataframe containing the whole infile content
        - n_cores: Integer indicating the number of cores used in the multiprocessing

    Output: df_out: Pandas dataframe containing the whole infile content with the MC Tag 
    added in a new column
    '''

    logging.info("Start microbial compound tagging")

    # Get numpy array with microbial compound list
    microbial_list = readMicrobialTable(args.microbialList)

    # Tagging without parallel process (AVOID MEMORY ERROR)
    # df_out = microbialTaggerBatch(df, microbial_list)

    # Split dataframe so that each batch is processed by one core
    df_split = np.array_split(df, n_cores)

    # Create list with parameters received by each drugTaggerBatch function in each subprocess
    subprocess_args = [(df_i, microbial_list) for df_i in df_split]

    with Pool(n_cores) as p:

        logging.info("Tagging microbial compounds")
        result = p.starmap(microbialTaggerBatch, subprocess_args)
        df_out = pd.concat(result)

    logging.info("Finished microbial tagging")

    return df_out


def readPlantTable(path):
    '''
    Input:
        - path: String containing the path to the plant database
    
    Output:
        - plant_list: String Numpy Array containing plant name extracted from the database
    '''

    logging.info(f"Reading Plant Table: {path}")

    # Import drug table as a pandas dataframe
    df = pd.read_csv(path, header=0, sep="\t", dtype=str)

    # Extract drug list name from df as a numpy array
    plant_list = np.array(df.iloc[:, 0])

    return plant_list


def plantTaggerBatch(df, plant_list):
    '''
    Input:
        - df: Pandas dataframe containing a batch of the whole infile dataframe
        - plant_list: String Numpy Array containing all plant compounds in the database
    
    Output:
        - df: Pandas dataframe with the plant tag added in a new column
    '''

    # Get numpy array with compound in input table
    compound_names = np.array(df.loc[:, 'Name']) 

    # Tag corresponding compounds
    plant_tag = ["" if pd.isna(compound) else "Plant" if getFirstSynonym(compound) in plant_list else "" for compound in compound_names]

    # Add Plant tag column to the dataframe
    name_column_index = getNameColumnIndex(df.columns)
    df.insert(name_column_index+1, "Plant", plant_tag, True)
    
    return df


def plantTagger(df, n_cores):
    '''
    Input:
        - df: Pandas dataframe containing the whole infile content
        - n_cores: Integer indicating the number of cores used in the multiprocessing

    Output: df_out: Pandas dataframe containing the whole infile content with the Plant Tag 
    added in a new column
    '''

    logging.info("Start plant compound tagging")

    # Get numpy array with microbial compound list
    plant_list = readPlantTable(args.plantList)

    # Split dataframe so that each batch is processed by one core
    df_split = np.array_split(df, n_cores)

    # Create list with parameters received by each drugTaggerBatch function in each subprocess
    subprocess_args = [(df_i, plant_list) for df_i in df_split]

    with Pool(n_cores) as p:

        logging.info("Tagging plant compounds")
        result = p.starmap(plantTaggerBatch, subprocess_args)
        df_out = pd.concat(result)

    logging.info("Finished plant tagging")

    return df_out


def npTaggerBatch(df, np_list):
    '''
    Input:
        - df: Pandas dataframe containing a batch of the whole infile dataframe
        - np_list: String Numpy Array containing all natural products in the database
    
    Output:
        - df: Pandas dataframe with the NP tag added in a new column
    '''

    # Get numpy array with compound in input table
    compound_names = np.array(df.loc[:, 'Name']) 

    # Tag corresponding compounds
    np_tag = ["" if pd.isna(compound) else "NP" if getFirstSynonym(compound) in np_list else "" for compound in compound_names]

    # Add Drug tag column to the dataframe
    name_column_index = getNameColumnIndex(df.columns)
    df.insert(name_column_index+1, "NaturalProduct", np_tag, True)
    
    return df


def readNPTable(path):
    '''
    Input:
        - path: String containing the path with the food containing table
    
    Output:
        - np_list: Numpy array of strings containing all natural products in the table
    '''

    logging.info(f"Reading Natural Product Table: {path}")

    df = pd.read_csv(path, header=0, sep="\t", dtype=str)
    np_list = np.array(df.iloc[:, 0].drop_duplicates(keep='first', inplace=False))

    return np_list


def npTagger(df, n_cores):
    '''
    Input:
        - df: Pandas dataframe containing the whole infile content
        - n_cores: Integer indicating the number of cores used in the multiprocessing

    Output: df_out: Pandas dataframe containing the whole infile content with the NP Tag 
    added in a new column
    '''

    logging.info("Start natural products tagging")

    # Split dataframe so that each batch is processed by one core
    df_split = np.array_split(df, n_cores)

    # Get numpy array with drug list
    np_list = readNPTable(args.naturalList)

    # Create list with parameters received by each drugTaggerBatch function in each subprocess
    subprocess_args = [(df_i, np_list) for df_i in df_split]

    with Pool(n_cores) as p:

        logging.info("Tagging natural products")
        result = p.starmap(npTaggerBatch, subprocess_args)
        df_out = pd.concat(result)
    
    logging.info("Finished natural products tagging")

    return df_out


def halogenatedTaggerBatch(df, halogen_regex):
    '''
    Input:
        - df: Pandas dataframe corresponding to a batch of the infile table
        - halogen_regex: String corresponding to the regular expression used to identify halogenated compounds
    
    Output:
        - df: Pandas dataframe with Halogenated tag added in a new column
    '''

    # Extract compound names
    compound_names = np.array(df.loc[:, 'Name'])

    # Check if there is a column with molecular formula
    formulaColumn = [colName for colName in df.columns if re.search(r"(?i)^formula$", colName)]

    # Extract compound formula if possible
    compound_formula = np.array(df.loc[:, formulaColumn[0]]) if len(formulaColumn) != 0 else []


    # Tag corresponding compounds
    if len(formulaColumn) == 0:
        # there is no formula column, so we look for regex in compound names
        halogenated_tag = ["" if pd.isna(compound) else "x" if (re.search(halogen_regex, compound)) else "" for compound in compound_names]

    else:
        # there is formula column, so we look for regex in formula (and compound names if there is no formula)

        halogenated_tag = []

        for formula, compound in zip(compound_formula, compound_names):

            if not pd.isna(formula):
                # formula is not nan
                halogenated_tag.append('x') if re.search(r'(F|Cl|Br|I)(?![a-z])', formula) else halogenated_tag.append("")
            
            elif not pd.isna(compound):
                # formula is nan but compound is not
                halogenated_tag.append('x') if re.search(halogen_regex, compound) else halogenated_tag.append("")
            
            else:
                # formula and compound are nan
                halogenated_tag.append("")

    # Add Drug tag column to the dataframe
    name_column_index = getNameColumnIndex(df.columns)
    df.insert(name_column_index+1, "Halogenated", halogenated_tag, True)
    
    return df


def halogenatedTagger(df, n_cores):
    '''
    Input:
        - df: Pandas dataframe containing the whole content present in infile table
        - n_cores: Integer indicating the number of cores used in the multiprocessing
    
    Output:
        - df_out: Pandas dataframe with halogenated tag added in a new column
    '''

    logging.info("Start halogenated compounds tagging")

    # Get string with the regular expression used to identify halogenated compounds
    halogen_regex = config_param.get('Parameters', 'HalogenatedRegex')

    # Tagg without parallel process (AVOID MEMORY ERROR)
    # df_out = halogenatedTaggerBatch(df, halogen_regex)

    # Split dataframe so that each batch is processed by one core
    df_split = np.array_split(df, n_cores)

    # Create list with parameters received by halogenatedTaggerBatch in each subprocess
    subprocess_args = [(df_i, halogen_regex) for df_i in df_split]

    with Pool(n_cores) as p:

        logging.info("Tagging halogenated compounds")
        result = p.starmap(halogenatedTaggerBatch, subprocess_args)
        df_out = pd.concat(result)
    
    logging.info("Finished halogenated compounds tagging")

    return df_out 


def peptideTaggerBatch(df, peptide_regex):
    '''
    Input:
        - df: Pandas dataframe corresponding to a batch of the infile table
        - peptide_regex: String corresponding to the regular expression used to identify peptide compounds
    
    Output:
        - df: Pandas dataframe with Halogenated tag added in a new column
    '''

    # Get numpy array with compound in input table
    compound_names = np.array(df.loc[:, 'Name']) 

    # Tag corresponding compounds
    peptide_tag = ["" if pd.isna(compound) else "Pep" if re.search(peptide_regex, compound) else "" for compound in compound_names]

    # Add Drug tag column to the dataframe
    name_column_index = getNameColumnIndex(df.columns)
    df.insert(name_column_index+1, "Peptide", peptide_tag, True)
    
    return df


def peptideTagger(df, n_cores):
    '''
    Input:
        - df: Pandas dataframe containing the whole content present in infile table
        - n_cores: Integer indicating the number of cores used in the multiprocessing
    
    Output:
        - df_out: Pandas dataframe with peptide tag added in a new column
    '''

    logging.info("Start peptide compounds tagging")

    # Get string with the regular expression used to identify peptide compounds
    # peptide_regex = "(?i)^(Ala|Arg|Asn|Asp|Cys|Gln|Glu|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val|[-\s,]){3,}$"
    peptide_regex = config_param.get('Parameters', 'PeptideRegex')

    # Tag without parallel process (AVOID MEMORY ERROR)
    # df_out = peptideTaggerBatch(df, peptide_regex)

    
    # Split dataframe so that each batch is processed by one core
    df_split = np.array_split(df, n_cores)

    # Create list with parameters received by peptideTaggerBatch in each subprocess
    subprocess_args = [(df_i, peptide_regex) for df_i in df_split]

    with Pool(n_cores) as p:

        logging.info("Tagging peptides")
        result = p.starmap(peptideTaggerBatch, subprocess_args)
        df_out = pd.concat(result)
    
    logging.info("Finished peptide tagging")

    return df_out    


def getOutputFilename():
    '''
    Output:
        - filename: String containing the name of the output file
    '''

    filename = config_param.get('Parameters', 'OutputName')
    filename = os.path.splitext(filename)[0] + '.xlsx'

    if not filename:
        filename = 'tagged_' + os.path.basename(args.infile)

    if not os.path.splitext(filename)[1]:
        filename += '.xlsx'
    
    return filename


def getOutputColumns(df_columns):
    '''
    Input:
        - df_columns: Pandas series containing the name of the columns in the output table
    
    Output:
        - selected_columns: List of strings with the name of the columns selected by the user
    '''

    selected_columns = config_param.get('Parameters', 'OutputColumns')

    if selected_columns:
        selected_columns = [column.strip() for column in selected_columns.split(',') if column.strip() in df_columns]
    
    else:
        selected_columns = list(df_columns)
    
    return selected_columns


def writeDataFrame(df, path):
    '''
    Description: Function used to export pandas dataframe with the tags added

    Input:
        - df: Pandas dataframe that will be exported
        - path: String containing the path to outdir. The new file will be saved in the
        same folder.
    '''

    # Build output file path
    # output_path = os.path.join(os.path.dirname(path), "results")
    # output_path = os.path.dirname(path)
    output_path = path
    
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
    
    # Get output file name
    filename = getOutputFilename()

    output_file = os.path.join(output_path, filename)

    # Get output columns
    output_columns = getOutputColumns(df.columns)

    # Handle errors in exception case
    try:
        df.to_excel(output_file, index=False, columns=output_columns, engine="openpyxl")
    
    except:
        log_str = f'Error when writing {str(Path(output_file))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'{exctype}: {value}'
        logging.info(log_str)

        sys.exit(12)
    
    log_str = f'Write Output Table: {str(Path(output_file))}'
    logging.info(log_str)



#################
# Main function #
#################

def main(args):
    '''
    Main function
    '''

    # Number of cores used
    n_cores = min([args.cpuCount, cpu_count()])
    logging.info(f"Using {n_cores} cores")

    # Read infile
    df = readInfile(args.infile, 0)

    # Check user selection
    if re.search('(?i)true', config_param['TagSelection']['Food']):
        df = foodTagger(df, n_cores)
    
    if re.search('(?i)true', config_param['TagSelection']['Drug']):
        df = drugTagger(df, n_cores)
    
    if re.search('(?i)true', config_param['TagSelection']['MicrobialCompound']):
        df = microbialTagger(df, n_cores)

    if re.search('(?i)true', config_param['TagSelection']['Plant']):
        df = plantTagger(df, n_cores)

    # if re.search('(?i)true', config_param['TagSelection']['NaturalProduct']):
    #    df = npTagger(df, n_cores)

    if re.search('(?i)true', config_param['TagSelection']['Halogenated']):
        df = halogenatedTagger(df, n_cores)
    
    if re.search('(?i)true', config_param['TagSelection']['Peptide']):
        df = peptideTagger(df, n_cores)
    
    # Export dataframe as excel file
    writeDataFrame(df, args.outdir)
    


if __name__=="__main__":

    multiprocessing.freeze_support()

    # parse arguments
    parser = argparse.ArgumentParser(
        description='Tagger',
        epilog='''
        Example:
            python Tagger.py
        
        '''
    )

    # Set default values
    default_config_path = os.path.join(os.path.dirname(__file__), '..', 'config' , 'configTagger', 'configTagger.ini')
    default_food_list_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'food_database.tsv')
    default_drug_list_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'drug_database.tsv')
    default_microbial_compound_list_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'microbial_database.tsv')
    default_natural_products_list_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'natural_product_database.tsv')
    default_plant_list_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'plant_database.tsv')

    # Parse arguments corresponding to path files
    parser.add_argument('-i', '--infile', help="Path to input file", type=str, required=True)
    parser.add_argument('-c', '--config', help="Path to configTagger.ini file", type=str, default=default_config_path)
    parser.add_argument('-fL', '--foodList', help="Path to food compounds list", type=str, default=default_food_list_path)
    parser.add_argument('-dL', '--drugList', help="Path to drug compounds list", type=str, default=default_drug_list_path)
    parser.add_argument('-mL', '--microbialList', help="Path to microbial compounds list", type=str, default=default_microbial_compound_list_path)
    parser.add_argument('-npL', '--naturalList', help="Path to natural products list", type=str, default=default_natural_products_list_path)
    parser.add_argument('-pL', '--plantList', help="Path to plant list", type=str, default=default_plant_list_path)

    parser.add_argument('-o', '--output', help="Name of output table", type=str)
    parser.add_argument('-od', '--outdir', help="Path to output dir", type=str, default=Path('.'))
    parser.add_argument('-oc', '--outCol', help='Name of columns present in output table. By default, all columns will be displayed', type=str)

    parser.add_argument('-cpu', '--cpuCount', help='Number of cores used in the processing', default=1, type=int)

    # Parser arguments indicating which tags are going to be added
    parser.add_argument('-f', '--food', help="Add food tag to compounds", action='store_true')
    parser.add_argument('-d', '--drug', help="Add drug tag to compounds", action='store_true')
    parser.add_argument('-m', '--microbial', help="Add 'microbial compound' tag to compounds", action='store_true')
    parser.add_argument('-ha', '--halogenated', help="Add 'halogenated compound' tag to compounds", action='store_true')
    parser.add_argument('-np', '--natural', help="Add NP tag to compounds", action='store_true')
    parser.add_argument('-p', '--peptide', help="Add Peptide tag to compounds", action='store_true')
    parser.add_argument('-pn', '--plant', help="Add Plant tag to compounds", action='store_true')

    parser.add_argument('-v', dest='verbose', action='store_true', help='Increase output verbosity')
    args = parser.parse_args()

    # parse config with user selection
    config_param = configparser.ConfigParser(inline_comment_prefixes='#')
    config_param.read(Path(args.config))

    # Parameters introduced in the execution replace those in the .ini file
    if args.food:
        config_param.set('TagSelection', 'Food', str(args.food))

    if args.drug:
        config_param.set('TagSelection', 'Drug', str(args.drug))

    if args.microbial:
        config_param.set('TagSelection', 'MicrobialCompound', str(args.microbial))

    if args.halogenated:
        config_param.set('TagSelection', 'Halogenated', str(args.halogenated))
    
    if args.natural:
        config_param.set('TagSelection', 'NaturalProduct', str(args.natural))

    if args.plant:
        config_param.set('TagSelection', 'Plant', str(args.plant))

    if args.output:
        config_param.set('Parameters', 'OutputName', args.output)
    
    if args.outCol:
        config_param.set('Parameters', 'OutputColumns', args.outCol)



    # logging debug level. By default, info level
    if args.infile:
        log_file = outfile = os.path.splitext(args.infile)[0] + '_log.txt'
        log_file_debug = outfile = os.path.splitext(args.infile)[0] + '_log_debug.txt'
    
    else:
        log_file = outfile = 'log.txt'
        log_file_debug = outfile = 'log_debug.txt'


    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            handlers=[logging.FileHandler(log_file_debug),
                                      logging.StreamHandler()])
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            handlers=[logging.FileHandler(log_file),
                                      logging.StreamHandler()])

    
    # start main function
    logging.info('start script: '+"{0}".format(" ".join([x for x in sys.argv])))
    main(args)
    logging.info('end script')