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
import pandas as pd
import numpy as np
import re
import csv
import json
from pygoslin.parser.Parser import LipidParser
import multiprocessing
from multiprocessing import Pool, cpu_count

import pdb

###################
# Local functions #
###################

class NoNameColumn(Exception):
    pass

class NoExperimentalMassColumn(Exception):
    pass


def readLipidList(infile_path):
    '''
    Description: readLipidList reads goslin lipid list in csv format. The fucntion
    will create a list with lipid names in first columns, and all its synonyms,
    iterating over all rows.

    Input:
        - infile_path: Path where csv lipid list can be found
    Output:
        - lipid_list: List of strings with all lipid names
    '''

    with open(infile_path, 'r') as infile:

        line = infile.readline() # skip title row
        lipid_reader = csv.reader(infile, delimiter=',', quotechar='"')

        lipid_list = []
        for row in lipid_reader:
            if len(row) > 0 and len(row[0]) > 0:
                lipid_list.append(row[0])
                lipid_list.extend([r for r in row[6:] if len(r) > 0])
    
    return lipid_list


def readSynonyms(infile_path):
    """
    Input:
        - infile_path: String containing path to synonyms.json
    Output:
        - synonyms_dict_lower: Dictionary containing synonyms relations
    """

    with open(infile_path, 'r') as infile:
        synonyms_dict = json.load(infile)
    
    synonyms_dict_lower = {re.sub(r'[-\s()[\]{}]', '', key.lower()):synonyms_dict[key] for key in synonyms_dict}

    return synonyms_dict_lower


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
        
        if "Experimental mass" not in df.columns:
            raise NoExperimentalMassColumn("ERROR: 'Experimental mass' column was not found")
    
        # Make sure that all column names are string
        df.rename(columns={name: str(name) for name in df.columns}, inplace=True)
    

    except NoNameColumn:
        log_str = f'Error when reading {str(Path(infile))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'NoNameColumn: {value}'
        logging.info(log_str)

        sys.exit(210) # Status code for column name error

    except NoExperimentalMassColumn:
        log_str = f'Error when reading {str(Path(infile))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'NoExperimentalMassColumn: {value}'
        logging.info(log_str)

        sys.exit(211) # Status code for column name error
    
    except:
        log_str = f'Error when reading {str(Path(infile))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'{exctype}: {value}'
        logging.info(log_str)

        sys.exit(20) # Status code for file format
    

    log_str = f'{str(Path(infile))} was read'
    logging.info(log_str)

    return df


def removeRow(df_row, name_col_index, regex):
    '''
    Input:
        - df_row: Row of pandas dataframe received in the apply
        - name_col_index: Index of compound name
        - regex: Regular expression applied to compound name string
    Output:
        - True if regex is found and False otherwise.
    '''
    
    compound_name = df_row.iat[name_col_index]

    return bool(re.search(regex, compound_name))


def splitCompoundField(compound_name, regex_sep):
    '''
    Description: parseCompoundList receives the string present in the field
    corresponding to the compound name. It splits the string into the different
    compounds names using separator regex given by the user.

    Input:
        - compound_name: String with compound names that may be separated
        - regex_sep: String with regular expression with possible separators
    
    Output:
        - compound_list: List of different compounds
        - separator: String with the separator found for the compounds
    '''

    match_sep = re.search(regex_sep, compound_name)

    # If there is match, make split. Else, return a list with the single compound
    if match_sep is not None:
        separator = match_sep.group()
        compound_list = re.split(separator, compound_name)
    
    else:
        separator = ''
        compound_list = [compound_name]
    
    return compound_list, separator


def synonymSub(df_row, name_col_index, regex_sep, synonyms_dict):
    """
    Input:
        - df_row: Pandas dataframe row
        - name_col_index: Integer corresponding to index of column containing names
        - regex_sep: String with regex containing possible separators
        - synonym_dict: Dictionary with synonyms
    Output: 
        - df_row_out: Pandas dataframe row
    """

    df_row_out = df_row.copy()

    # Extract compound name
    compound = df_row_out.iat[name_col_index]

    # Split into different compounds
    compound_list, separator = splitCompoundField(compound, regex_sep)

    # Substitute by the synonym, re-join and write in the row
    compound_list = [synonyms_dict[re.sub(r'[-\s()[\]{}]', '', compound.lower())] \
        if re.sub(r'[-\s()[\]{}]', '', compound.lower()) in synonyms_dict else compound for compound in compound_list]

    compound = separator.join(compound_list)
    
    df_row_out.iat[name_col_index] = compound

    return df_row_out


def subProcessSynonym(df_i, name_col_index, synonym_dict, regex_sep):
    """
    Input:
        - df_i: Pandas dataframe (batch)
        - name_col_index: Integer corresponding to index of column containing compound names
        - synonym_dict: Dictionary with synonyms
    Output:
        - df_i_out: Pandas dataframe returned
    """
    
    df_i_out = df_i.apply(func=synonymSub, axis=1, args=(name_col_index, regex_sep, synonym_dict))
    return df_i_out

    
def synonymsSubstitution(df, name_col_index, synonyms_dict, regex_sep, n_cores):
    """

    """

    # SUBSTIUTE WITHOUT PARALLEL PROCESS (AVOID MEMORY ERROR)
    df_processed = subProcessSynonym(df, name_col_index, synonyms_dict, regex_sep)

    '''
    # Split dataframe so that each is processed by one core
    df_split = np.array_split(df, n_cores)

    # Create list of tuples. Each tuple contains arguments received by subProcessFunctionLipid
    subprocess_args = [(df_i, name_col_index, synonyms_dict, regex_sep) for df_i in df_split]

    with Pool(n_cores) as p:
        result = p.starmap(subProcessSynonym, subprocess_args)
        df_processed = pd.concat(result)
    '''
    
    return df_processed



def parseCompoundList(compound_list, regex, replace):
    '''
    Description: parseCompoundList applies the transformation to each compound in the list

    Input:
        - compound_list: List of strings, with the name of the compounds
        - regex: String with the regular expression applied
        - replace: String with the value that will replace the recognized pattern
    Output:
        - List of strings with the parsed compounds
    '''

    return [re.sub(regex, replace, compound.strip()) for compound in compound_list]


def parserCompound(compound_name, regex, replace, regex_sep):
    '''
    Description: parserCompound apply a regular expression to the row received, replacing the
    recognized patter by the value given in 'replace'
    
    Input:
        - df_row: Series (row) from the pandas dataframe
        - name_col_index: Integer with the name column index (0-based)
        - regex: String with the regular expression
        - replace: String with the value that replaces the pattern
        - regex_sep: Separator between compounds within a field
    Output:
        - df_row_out: Series (row) transformed
    '''


    # Obtain a list with different compounds names within the field (one or more)
    compound_list, separator = splitCompoundField(compound_name, regex_sep)

    # Apply the transformation to each compound of the field (they are in the list)
    parsed_compound_list = parseCompoundList(compound_list, regex, replace)

    parsed_compound_name = separator.join(parsed_compound_list)

    return parsed_compound_name


"""
def immunityExtractor(compound_name):
    '''
    Input:
        - compound_name: String with the compound name
    Output:
        - compound_name: String with compound name with ##%% tags
        - immune_list: List with substrings extracted from ##%%
    '''

    # Store all immune substrings
    immune_list = []
    pos = 0

    # Capture immune substring
    newStart = 0
    re_immune = re.search(r'##[^#%]+%%', compound_name)

    # Keep capturing until the last
    while re_immune:
        immune_list.append(re_immune.group()[2:-2])

        # Replace the substring by the tag ##pos%%
        compound_name = compound_name[:newStart] + re.sub(f'##[^#%]+%%', f'##{pos}%%', compound_name[newStart:], 1)
        pos += 1

        # Search with new start considering the replacements
        newStart = re_immune.span()[0]+4+len(str(pos))
        re_immune = re.search(r'##[^#%]+%%', compound_name[newStart:])
       
    return compound_name, immune_list


def immunityRecoverer(compound_name, immune_list):
    '''
    Input:
        - compound_name: String containing the compound name
        - immune_list: List with immune substrings
    Output:
        - compound_name: String with restored immune substrings
    '''

    re_immune = re.search(r'##(\d+)%%', compound_name)
    
    while re_immune:
        # Get the immune group position and replace
        pos = int(re_immune.groups()[0])
        compound_name = re.sub(re_immune.group(), immune_list[pos], compound_name, 1)

        # Search again with newStart considering the replacement
        newStart = re_immune.span()[0] + len(immune_list[pos])
        re_immune = re.search(r'##(\d+)%%', compound_name[newStart:])

    return compound_name
"""

def parserTable(df_row, name_col_index, regex_sep, config_regex):
    '''
    Description: The function applies each regular expression to the row received (df_row). These
    regular expressions are stored in config_regex. With a loop we iterate over each regex and its
    replacement. Then, we call parserCompound function to apply  each transformation.

    Input:
        - df_row: Pandas series with the row being processed
        - name_col_index: Integer corresponding to the index of the column name
        - regex_sep: String corresponding to the compound separator in name field
    Output:
        - df_row_out: Pandas series corresponding to the modified row
    '''

    df_row_out = df_row.copy()
    compound_name = df_row.iat[name_col_index]

    # Parse compound name to "protect" part of the string with with immunity tag "##substring%%"
    # compound_name, immune_list = immunityExtractor(compound_name)

    if re.search('^###[^#]+###$', compound_name):
        # if compound name has been processed by goslin, remove "###" tag and return it
        df_row_out.iat[name_col_index] = compound_name[3:-3]
        return df_row_out


    # Iterate over each regular expresion
    for regex_section in config_regex.sections():

        # It gives a list with the two values of the section
        regex, replace = [config_regex[regex_section][option] for option in config_regex[regex_section]._options()]

        # Parse the row using parserCompound
        compound_name = parserCompound(compound_name, regex, replace, regex_sep)
    
    # Parse compound name to add the immune substrings extracted previously
    # compound_name = immunityRecoverer(compound_name, immune_list)

    df_row_out.iat[name_col_index] = compound_name
    
    return df_row_out


def isPeptide(aa_list):
    '''
    Description: isPeptide receives a list of strings obtained from splitting a compound name by the aminoacid
    separator given by the user. If all strings are aminoacids it is returned True. Otherwise, it returns False.
    '''

    aminoacids = ["Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile", \
        "Leu", "Lys", "Met", "Phe", "Pro", "Ser", "Thr", "Trp", "Tyr", "Val"]

    return np.all([aa in aminoacids for aa in aa_list])


def sortPeptides(df_row, name_col_index, aa_sep):
    '''
    Description: sortPeptides split compound name by aminoacid separator and asserts that it is
    a peptide. If so, peptide aminoacids are sorted and joined by the separator. It is returned
    the processed row, with the sequence of both, the sorted peptide, and the original one, separated
    by the label '#####'
    '''

    df_row_out = df_row.copy()

    compound_name = df_row.iat[name_col_index] # Extract compound name

    # Split peptide in aminoacids
    aa_list, separator = splitCompoundField(compound_name, aa_sep)

    if isPeptide(aa_list):
        aa_sorted_list = sorted(aa_list)
        compound_name_out = separator.join(aa_sorted_list) + '#####' + separator.join(aa_list)
        df_row_out.iat[name_col_index] = compound_name_out

    return df_row_out


def lipidPreProcess(compound):
    '''
    Description: Compound names is parsed removing the information that cannot be processed by Goslin.
    
    Input:
        - compound_out: String with the name of the compounds
    Output:
        - compound_out: String with the parsed name of the compounds
    '''

    # Remove information between [ ]
    compound_out = re.sub(r'\[\w+\]', '', compound)

    # Remove 'i-' 'a-' information. There must be a '(' or '/' before it, and a number after it: TG(i-13:0/i-14:0/8:0)
    compound_out = re.sub(r'(?<=[\(/])[ia]-(?=\d)', '', compound_out)

    # Remove synonym after \n (in some FAHFA compounds)
    compound_out = re.sub(r'\n.*$', '', compound_out)

    return compound_out


def getHeaderGroup(lipid):
    '''
    Description: Get head group from lipid, and in case it begins with Lyso, replace
    by L
    
    Input:
        - lipid: Lipid object from Goslin library
    Output:
        - head_group: String with head group
    '''

    head_group = lipid.lipid.head_group
    head_group = re.sub(r'(?i)^Lyso', 'L', head_group)

    return head_group


def getCarbonAtoms(lipid):
    '''
    Input:
        - lipid: Lipid object from Goslin library
    Output:
        - Integer with total number of carbon atoms in fatty acids present in lipids
    '''

    fa_num_carbon_list = np.array([fa.num_carbon for fa in lipid.lipid.fa_list])
    return np.sum(fa_num_carbon_list)


def getDoubleBonds(lipid):
    '''
    Input:
        - lipid: Lipid object from Goslin library
    Output:
        - Integer with total number of double bonds in fatty acids present in lipids
    '''

    fa_num_double_bonds_list = np.array([fa.num_double_bonds for fa in lipid.lipid.fa_list])
    return np.sum(fa_num_double_bonds_list)


def getFaBondType(lipid):
    '''
    Description: getFaBondTyppe recognizes if any of the fatty acids in lipid has a plasmanyl (O-)
    or plasmenyl (P-) bond type. O- is associated to number 2 and P- to number 3 in Goslin. 1 would
    be ESTHER bond and 0 is undefined.

    Input:
        - lipid: Lipid object from Goslin library
    Output:
        - 'O-' if any 2
          'P-' if any 3
          '' else    
    '''

    fa_bond_type_list = np.array([fa.lipid_FA_bond_type.value for fa in lipid.lipid.fa_list])

    if 2 in fa_bond_type_list:
        return 'O-'
    
    elif 3 in fa_bond_type_list:
        return  'P-'
    
    else:
        return ''


def lipidCandidate(compound_name, lipid):
    '''
    Description: lipidCandidate returns True if lipid string is at the beginning
    of the compound name string.
    '''

    if re.match('^'+lipid, compound_name):
        return True
    
    else:
        return False


def isGoslinLipid(compound_name, lipid_list):
    '''
    Description: isGoslinLipid returns True is compound_name is in goslin lipid_list. Otherwise
    it will return False
    '''
    return np.any([lipidCandidate(compound_name, lipid) for lipid in lipid_list])


def FAHFA_parser(FAHFA_reObject):
    '''
    Input:
        - FAHFA_reObject: re object with the following structure:
            group 1 == 'FAHFA'
            group 2 == 'nC1:nDB1'
            group 3 == 'nC2:nDB2'
    Output: 
        - String: 'FAHFA(nC1+nC2:cDB1+nDB2)'
    '''
    
    # group 1 and 2 are "numberOfCarbon:numberOfDoubleBond". 
    cAtom_dBond = [int(n1) + int(n2) for n1, n2 in zip(FAHFA_reObject.group(2).split(':'), FAHFA_reObject.group(3).split(':'))]
    
    return f"###{FAHFA_reObject.group(1)}({cAtom_dBond[0]}:{cAtom_dBond[1]})###"


def hydroxylGeneratorList(compound):
    '''
    Input:
        - compound: string with lipid name
    Output:
        - list_OH: List of string with all matches
    '''

    regex = r'\(\d*OH(\[[\w,]+\])?\)'
    list_OH = []

    # Apply regex to compound
    re_OH = re.search(regex, compound)

    # Append all matches until the last one
    while re_OH:

        # Append the match
        list_OH.append(re_OH.group())

        # Define new start from which apply the regex
        new_start = re_OH.span()[1]

        # Apply the regex again
        re_OH = re.search(regex, compound[new_start:])

    return list_OH


def getHydroxyl(compound):
    '''
    Input:
        - compound: String with the lipid name
    Output:
        - String with the format: (nOH). Empty string if n = 0
    '''
    
    hydroxyl_list = hydroxylGeneratorList(compound)
    total_OH = 0

    for oh in hydroxyl_list:
        re_OH = re.search('\d+', oh)

        # If there is not a number, we assume it just one OH
        if not re_OH:
            total_OH += 1
            continue

        total_OH += int(re_OH.group())
    
    
    # If there is no OH, return empty string
    if total_OH == 0:
        return ""
    
    # Else, return the (nOH)
    # We write it between ## and %% to tag it. By this way, they will not be processed
    # by regular expressions later. It is a "immunity" label
    else:
        return "(" + str(total_OH) + "OH)"


def getMethyl(compound):
    '''
    Input:
        - compound: String containing compound name
    Output:
        - String added to new compound name
    '''

    # Regular expression used to match Me
    regex = r'\(\d+(\([RS]\))?Me\)'

    # Number of methyl groups detected
    n_methyl = 0

    re_Me = re.search(regex, compound)
    while re_Me:
        
        # Increment methyl group unit
        n_methyl += 1

        # Define new start in the string and apply regular expression again
        new_start = re_Me.span()[1]
        re_Me = re.search(regex, compound[new_start:])

    # Handle return depending on the number of Me groups detected
    if n_methyl == 0:
        return ""

    elif n_methyl == 1:
        return "(Me)"

    else:
        return f"({n_methyl}Me)"


def parserLipidCompound(compound, lipid_list):
    '''
    Description: parserLipidCompound parses the lipid name using Goslin library. First,
    it applies a filter using a regular expression, to avoid creating a goslin lipid object with all
    compounds, which will raise an error in most of the cases, making the code too slow. If the filter
    is passed, it creates the goslin lipid object, and then extract the required information from it.

    Input:
        - compound: String the compound name
    Output:
        - compound_out: String with the parsed (if possible) compound name
    '''

    # Apply a filter using LipidRegex in parameters.ini to make code faster
    if not isGoslinLipid(compound, lipid_list):
        return compound

    # Check if it is FAHFA. 'FAHFA(15:0-(18-O-22:0))' yields error due to '18-O-'.
    FAHFA_reObject = re.search(r'^(FAHFA)\((\d+:\d+)-\(\d+-O-(\d+:\d+)\)\)', compound)
    if FAHFA_reObject:
        return FAHFA_parser(FAHFA_reObject)

    # Pre-process compound name so that it can be recognized by goslin
    pre_proc_compound = lipidPreProcess(compound)

    try:
        # Create (if possible) Goslin lipid object from compound name
        lipid_parser = LipidParser()
        lipid = lipid_parser.parse(pre_proc_compound)

        # If lipid has no fatty  acid, return compound
        if lipid.lipid.fa_list == []:
            return compound

        # Get head group
        head_group = getHeaderGroup(lipid)

        # Get total number of carbon atoms
        n_carbon_atoms = getCarbonAtoms(lipid)

        # Get total number of double bonds
        n_double_bonds = getDoubleBonds(lipid)

        # Get FA bond type (plasmanyl/plasmenyl)
        fa_bond_type = getFaBondType(lipid)

        # If bond type is P-, goslin removes P and add one double bond. We undo this...
        n_double_bonds = (n_double_bonds - 1) if fa_bond_type == 'P-' else n_double_bonds

        # Get (OH) from lipid name to be maintained (done without Goslin): 
        # GlcCer(d14:1(4E)/22:0(2OH)) --> GlcCer(36:1(2OH))
        hydroxyl = getHydroxyl(compound)

        # Get Me from lipid name to be maintained (done without Goslin):
        # PE(18:0(10(R)Me)/16:0) --> PE(34:0(Me))
        methyl = getMethyl(compound)

        # Build lipid name using extracted information
        compound_out = '###' + head_group + '(' + fa_bond_type + str(n_carbon_atoms) + ':' + str(n_double_bonds) + methyl + hydroxyl + ')' '###'

        return compound_out

    except:
        # If gosling cannot parse the compound, it is returned without any change
        return compound


def parserLipidTable(df_row, name_col_index, regex_sep, lipid_list):
    '''
    Description: parserLipidTable is the function applied over the pandas dataframe.
    It receives each row, and process the compound name of lipids.

    Input:
        - df_row: Pandas series corresponding to a row of the dataframe
        - name_col_index: Integer corresponding to index of column name
        - regex_sep: String with compound separator in name field
        - lipid_regex: String with the regular expression used to identify lipids to be processed
    Output:
        - df_row_out: Output pandas series with the parsed name
    '''

    df_row_out = df_row.copy()

    # Get compound name
    compound_name = df_row.iat[name_col_index]

    # Obtain a list with different compounds names within the field (one or more)
    compound_list, separator = splitCompoundField(compound_name, regex_sep)

    # Parse each compound of the list, and join by the separator
    parsed_compound_list = [parserLipidCompound(compound, lipid_list) for compound in compound_list]
    parsed_compound_name = separator.join(parsed_compound_list)

    df_row_out.iat[name_col_index] = parsed_compound_name

    return df_row_out


def subProcessFuncRegex(df_i, name_col_index, regex_sep, aa_sep, config_regex):
    '''
    Description: Function executed using starmap() method from Pool. It receives chunks
    of dataframe, each of which are processed using apply. Dataframes are processed using
    regular expressions in the case of parserTable, and peptide aminoacids are sorted
    alphabetically in the case of sortPeptide.
    '''
    
    df_i_out = df_i.copy()

    # Parse dataframe using parserTable, which will iterates over the regular expressions
    df_i_out = df_i_out.apply(func=parserTable, axis=1, args=(name_col_index, regex_sep, config_regex))

    # Process peptides names, so that peptides with equal compoisition can be fused during the fusion
    df_i_out = df_i_out.apply(func=sortPeptides, axis = 1, args=(name_col_index, aa_sep))

    return df_i_out


def subProcessFuncLipid(df_i, name_col_index, regex_sep, lipid_list):
    '''
    Description: Function executed using starmap() method from Pool. It receives chunks of dataframe,
    processed using apply with parserLipidTable, which is going to process lipids with Goslin.
    '''
    
    df_i_out = df_i.copy()

    # Parse name of compound lipids in the dataframe using goslin (parserLipidTable)
    df_i_out = df_i_out.apply(func=parserLipidTable, axis=1, args=(name_col_index, regex_sep, lipid_list))

    return df_i_out


def sortIndexByName(df, name_col_index):
    '''
    Description: sortIndexByName sorts row indexes of pandas dataframe (df) using as reference
    the alphanumeric order of compound names. In this sense, indexes of rows with equal compound
    name will be together. Thanks to this, the comparison among rows during the fusion can be
    made faster, as we can compare one row with the following ones until the compound names 
    are different.

    Input:
        - df: Pandas dataframe with all data
        - name_col_index: integer with the position of the column containing compound names
    Output:
        - index_out: List of integers with the ordered indexes
    '''

    # Extract compound name column and row indexes
    compound_name = df.iloc[:, name_col_index]
    row_index = df.index.values

    # Create a list of tuples, where each tuple contains the row index and the compound name (lower)
    index_name_tuple_list = [(index, re.sub(r'[-\s()[\]{}]', '', name).lower()) for index, name in zip(row_index, compound_name)]

    # Sort tuples by second element, which is the compound name
    sorted_index_name_tuple_list = sorted(index_name_tuple_list, key=lambda x: x[1])

    # Extract indexes sorted by compound name
    index_out  = [index for index, name in sorted_index_name_tuple_list]

    return index_out


def getIndex(element, column_names):
    '''
    Description: getIndex receives an element (0-based index or name) associated to a column table. The function
    will return the 0-based index of that column.

    Input:
        - element: string with the 0-based index or name of the column
        - column_names: strings numpy array with the names of the columns
    Output:
        - out_element: Integer with the 0-based index of the column
    '''

    if re.match(r'^\d+$', element):
        out_element = int(element)
    
    elif element in column_names:
        out_element = int(np.where(column_names == element)[0][0])
    
    else:
        # If element is not among possible column names, return -1
        out_element = -1
    
    return out_element


def getColumnList(string_indexes, name_col_index, column_names):
    '''
    Description: getColumnList returns an array with the column indexes that are indicated
    by the user, without repeating the one with compound names

    Input:
        - string_indexes: String with comma-separated numbers, corresponding to the 0-based
        column index
        - name_col_index: Integer corresponding to the 0-based index of compound name column
        - column_names: strings numpy array with the names of the columns
    Output:
        - index_array: Numpy array with integers corresponding to 0-based integers
    '''

    # Split comma-separated elements given by the user
    index_array = np.array([getIndex(element.strip(), column_names) for element in string_indexes.split(',')])
    index_array = index_array[index_array != -1]

    # Remove index corresponding to column name
    index_array = index_array[index_array != name_col_index]

    return index_array


def getTagColumnNames(tag_str, column_names):
    '''
    Input:
        - tag_str: String containing tag containing column names separated by comma (',')
        - column_names: Pandas series containing all column names in infile
    Output:
        - tag_list: Numpy array containing tag containing column names
    '''

    tag_list = np.array([tag.strip() for tag in tag_str.split(',') if tag.strip() in column_names])

    return tag_list


def compareCompoundName(compound_name_i, compound_name_j):
    """
    Input:
        - compound_name_i: String containing upper compound name
        - compound_name_j: String containing downer compound name
    Output:
        - boolean: True if parsed are equal; False if they are different
    """

    parsed_i = re.sub(r'[-\s()[\]{}]', '', compound_name_i).lower()
    parsed_j = re.sub(r'[-\s()[\]{}]', '', compound_name_j).lower()
    
    return parsed_i == parsed_j


def combineConservedValues(conserved_values_i, conserved_values_j):
    '''
    Description: combineConservedValues receives two arrays of equal length. Each element 
    corresponds to a value of the row in one conserved field. The function will combine
    values of each field among both rows, i and j. In other words, value of j is added to i 
    (separated by ' // '), unless value of j is present in i.

    Input:
        - conserved_values_i: Array with values of upper row
        - conserved_values_j: Array with values of downer row
    Output:
        - conserved_out: List of strings with combined values for each field
    '''

    # Convert both arrays in str numpy  arrays
    conserved_values_i_str = np.array(conserved_values_i, dtype=str)
    conserved_values_j_str = np.array(conserved_values_j, dtype=str)

    # Zip function creates a list of tuple, where each tuple has i and j value for a given field.
    # It is iterated over different fields
    conserved_out = [field_i if field_j == '' else field_j if field_i == '' \
        else field_i + ' // ' + field_j if field_j not in field_i.split(' // ') else field_i \
        for field_i, field_j in zip(conserved_values_i_str, conserved_values_j_str)]
    
    return conserved_out


def fuseTable(df, name_col_index):
    '''
    Description: fuseTable compare each row of the pandas dataframe with downer rows, following
    the row order given by 'sorted_index'. If both rows have the same values for the comparing
    columns (given by the user), the downer row is removed/dropped. Values of the downer row present
    in conserved columns (also given by the user) are added to the values of the upper row
    (combineConservedValues). Using 'sorted_index' we iterate the rows following the alphanumeric 
    order of compound names, so we avoid comparing each row with all the rest. When upper row has
    finds a downer row with different compound name, we jump to next upper row.
    '''

    # Store column names in a numpy array
    column_names = np.array(df.columns, dtype=str)

    # Get information of the column with compound names (Index and column name)
    name_col_name = column_names[name_col_index]

    # Get lists with indexes and names corresponding to columns that will be compared
    compared_columns = getColumnList(args.compareCol, name_col_index, column_names)
    compared_columns_names = column_names[compared_columns]


    # Get lists with indexes and names corresponding to columns whose values will be conserved in the fusion
    conserved_columns = getColumnList(args.conserveCol, name_col_index, column_names)
    conserved_columns_names = column_names[conserved_columns] if len(conserved_columns) != 0 else []

    # Get list with the name of the columns containing tags of the compound
    tag_columns_names = getTagColumnNames(args.tagCol, df.columns)

    # Add columns containing tags to the set of conserving columns
    conserved_columns_names = np.concatenate((conserved_columns_names, tag_columns_names))

    # Get list with index of rows in the order over which they are going to be iterated
    sorted_index = sortIndexByName(df, name_col_index)

    # List with dropped-row indexes, to avoid their iteration
    removed_index = []

    # Loop upper row index
    for i, index_i in enumerate(sorted_index):

        # If upper row index was dropped, move to the next
        if index_i in removed_index:
            continue

        # Get string with compound name and array string with compared values, corresponding to upper row
        compound_name_i_original = str(df.at[index_i, name_col_name])
        compared_values_i = np.array([df.at[index_i, col] for col in compared_columns_names], dtype=str)

        # Variable to control when to move upper row to the next index (when i and j compound names are different)
        # continue_i = False

        # Loop over down row index
        for j, index_j in enumerate(sorted_index):
            
            # If down row index is below upper row index, or if it was dropped, move to the next
            if (j <= i) or (index_j in removed_index):
                continue

            # Get string with compound name and array string with compared values, corresponding to down row
            compound_name_i = compound_name_i_original  # In case compound_name_i was modified in previous iterations (peptides), we use the original
            compound_name_j = str(df.at[index_j, name_col_name])
            compared_values_j = np.array([df.at[index_j, col] for col in compared_columns_names], dtype=str)

            # If both are peptides, take only sorted name
            if ('#####' in compound_name_i) and ('#####' in compound_name_j):
                compound_name_i = compound_name_i.split('#####')[0]
                compound_name_j = compound_name_j.split('#####')[0]

            # If compound names are different, break downer loop, and move upper index to the next
            # if compound_name_i.lower().replace('-', '') != compound_name_j.lower().replace('-', ''):
            if not compareCompoundName(compound_name_i, compound_name_j):
                break

            # If any value in comparing field is different, move downer index to next
            elif np.any(compared_values_i != compared_values_j):
                continue

            # If all values in comparing field are the same, make the row fusion
            else:

                if len(conserved_columns_names) > 0:
                    # Get conserved values
                    conserved_values_i = ['' if pd.isna(df.at[index_i, col]) else df.at[index_i, col] for col in conserved_columns_names]
                    conserved_values_j = ['' if pd.isna(df.at[index_j, col]) else df.at[index_j, col] for col in conserved_columns_names]
                    
                    # Combine conserved values of i and j, and store them in upper row
                    df.loc[index_i, conserved_columns_names] = combineConservedValues(conserved_values_i, conserved_values_j)

                # Drop downer row and append its index to the removed_index list
                df.drop(axis=0, index=index_j, inplace=True)
                removed_index.append(index_j)

        # If i and j compound names were different, continue_i is True, so upper index move to the next
        # if continue_i:
        #    continue
    
    return df


def originalPeptides(df, name_col_index):
    '''
    Description: originalPeptides takes column name from the dataframe, and iterated over all of them. If label
    '#####' is in the compound name, it is taken the part of the name after it. By this way, it is taken the
    original peptide name, removing the sorted one.
    '''

    # Take compound name column as a list
    all_names = list(df.iloc[:, name_col_index])

    # Iterate over all names. If ##### is present, split and take the second part
    compound_name_out = [compound_name if '#####' not in compound_name else compound_name.split('#####')[1] for compound_name in all_names]

    # Restore compound name column
    df.iloc[:, name_col_index] = compound_name_out

    return df


def fuseByInChIKey(df, name_col_index):
    '''
    Input:
        - df: Pandas dataframe with Experimental mass, Name and InChIKey
    Output:
        - df: Pandas dataframe fused by InChiKey (if possible)
    '''
    inchikey_colname = "InChIKey"

    if inchikey_colname.lower() not in [col.lower() for col in df.columns]:
        # If InChIKey column is not in dataframe, return
        return df
    
    # get column name contained in df
    inchikey_colname = [col for col in df.columns if col.lower() == inchikey_colname.lower()][0]

    # Sort df indexes using InChIKey
    sorted_index_inchikey = sorted([[index, inchikey] for index, inchikey in zip(df.index.values, df.loc[:, inchikey_colname]) \
        if not pd.isna(inchikey)], key=lambda x: x[1])

    sorted_index_inchikey = [index for index, inchikey in sorted_index_inchikey]
    

    # Get compared columns names (excluding name)
    compared_columns_index = getColumnList(args.compareCol, name_col_index, df.columns.to_numpy())
    compared_columns_names = df.columns[compared_columns_index].to_list()

    # Get conserved column names (adding name)
    conserved_columns_index = getColumnList(args.conserveCol, name_col_index, df.columns.to_numpy())
    tag_columns_names = getTagColumnNames(args.tagCol, df.columns)
    tag_columns_index = [index for index, col in enumerate(df.columns) if col in list(tag_columns_names)]
    # conserved_columns_index = np.concatenate((conserved_columns_index, tag_columns_index, [name_col_index])).astype(int)
    conserved_columns_index = np.concatenate((conserved_columns_index, tag_columns_index)).astype(int)
    conserved_columns_names = df.columns[conserved_columns_index].to_list()

    removed_row_index = []
    for i, row_index_i in enumerate(sorted_index_inchikey):
        
        if row_index_i in removed_row_index:
            continue
        
        for j, row_index_j in enumerate(sorted_index_inchikey):

            if j <= i or row_index_j in removed_row_index:
                continue
            
            # Get InChIKey of both rows (14 first characters). If they are different, break
            inchikey_i = df.at[row_index_i, inchikey_colname][:14]
            inchikey_j = df.at[row_index_j, inchikey_colname][:14]

            if not inchikey_i == inchikey_j:
                break

            # Get compared values. If one field has different values, continue
            compared_values_i = df.loc[row_index_i, compared_columns_names]
            compared_values_j = df.loc[row_index_j, compared_columns_names]

            if any([i != j for i, j in zip(compared_values_i, compared_values_j)]):
                continue

            # At this line code, InChiKey and compared values are equal
            # Drop down line and move its name and conserved values to upper row

            conserved_values_i = df.loc[row_index_i, conserved_columns_names] # Get values and replace na by ""
            conserved_values_i[pd.isna(conserved_values_i)] = ""

            conserved_values_j = df.loc[row_index_j, conserved_columns_names]
            conserved_values_j[pd.isna(conserved_values_j)] = ""

            df.loc[row_index_i, conserved_columns_names] = combineConservedValues(conserved_values_i, conserved_values_j)

            # Drop downer row and append its index to the removed_index list
            df.drop(axis=0, index=row_index_j, inplace=True)
            removed_row_index.append(row_index_j)
    
    return df



def getOutFileName(infile):
    '''
    Description: getOutFileName generate a string with the output filename. If user did not specified the output
    filename in OutputName of parameters.ini, the name will be 'mod_'+infile. Besides, the function tests if
    the output file name given by the user has extension. If not, .xls will be used.
    '''

    filename = config_param['Parameters']['OutputName']
    filename = os.path.splitext(filename)[0] + '.xlsx'

    if not filename:
        filename = 'REnamed_' + infile
    
    if not os.path.splitext(filename)[1]:
        filename += '.xlsx'
    
    return filename


def getOutColumns(column_names):
    '''
    Description: getOutColumns receives a numpy array with the names of the columns. It returns
    the name of those columns selected by the user.
    '''

    out_columns = config_param['Parameters']['OutputColumns']

    if out_columns: 
        out_columns_index = getColumnList(string_indexes=out_columns, name_col_index=None, column_names=column_names)
        out_columns_name = column_names[out_columns_index]
    
    else:
        out_columns_name = column_names
    
    return out_columns_name


def writeDataFrame(df, path):
    '''
    Description: The function will write the padas dataframe in a 
    result folder using pandas.to_excel method.

    Input:
        - df: Pandas dataframe that is going to be written
        - path: Infile path given by the user
    '''

    # Build path of output file, including dir and name
    # output_path = os.path.join(os.path.dirname(path), 'results')
    # output_path = os.path.dirname(path)
    output_path = path
    
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)

    output_filename = getOutFileName(os.path.basename(args.infile))
    output_path_filename = os.path.join(output_path, output_filename)

    # Get output columns
    out_columns_name = getOutColumns(np.array(df.columns))

    # logging.info(f'Writing output table in {output_path_filename}')
    
    # Handle errors in exception case
    try:
        df.to_excel(output_path_filename, index=False, columns=out_columns_name, engine="openpyxl")
    
    except:
        log_str = f'Error when writing {str(Path(output_path_filename))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'{exctype}: {value}'
        logging.info(log_str)

        sys.exit(22)
    
    log_str = f'Write Output Table: {str(Path(output_path_filename))}'
    logging.info(log_str)

    return True


##################
# Main functions #
##################

def main(args):
    '''
    Main function
    '''
    
    # Number of cores. This should be a user variable
    n_cores = min([args.cpuCount, cpu_count()])
    logging.info(f"Using {n_cores} cores")

    # Store compound name column index
    # name_col_index = args.column      # Column containing compound names (0-based)
    header_index = args.row           # Row at which table begins (0-based)

    regex_remove = config_param['Parameters']['RemoveRow']
    regex_sep = config_param['Parameters']['Separator']
    aa_sep = config_param['Parameters']['AminoAcidSeparator']

    # Read goslin lipid list in csv format
    lipid_list = readLipidList(args.liplist)
    
    # Read JSON file containing compound synonyms
    synonyms_dict = readSynonyms(args.synonyms)
    
    # Read table as pandas data frame
    df = readInfile(args.infile, header_index)

    name_col_index = [index for index, col_name in enumerate(df.columns) if str(col_name).lower() == 'name'][0]

    # Remove rows given by RemoveRow regular expression
    logging.info("Removing rows identified by RemoveRow parameter")
    remove_row_bool = df.apply(func=removeRow, axis=1, args=(name_col_index, regex_remove))
    df.drop(axis=0, index=np.where(remove_row_bool)[0], inplace=True)

    # Synonym substitution prior to parsing
    logging.info(f'Synonyms substitution prior to parsing')
    df_processed = synonymsSubstitution(df, name_col_index, synonyms_dict, regex_sep, n_cores)

    # PARSE WITH GOSLIN WITHOUT PARALLEL PROCESS (AVOID MEMORY ERROR)
    logging.info(f'Parsing lipid names using Goslin')
    df_processed = subProcessFuncLipid(df_processed, name_col_index, regex_sep, lipid_list)
    
    '''
    # Split dataframe so that each is processed by one core
    df_split = np.array_split(df_processed, n_cores)

    # Create list of tuples. Each tuple contains arguments received by subProcessFunctionLipid
    subprocess_args = [(df_i, name_col_index, regex_sep, lipid_list) for df_i in df_split]

    with Pool(n_cores) as p:
        # logging.info(f'Parsing lipid names using Goslin')
        result = p.starmap(subProcessFuncLipid, subprocess_args)
        df_processed = pd.concat(result)
    '''

    # Fuse rows with the same value for the selected columns
    logging.info(f'Collapsing rows after lipid processing')
    df_processed = fuseTable(df_processed, name_col_index)
    
    # APPLY REGULAR EXPRESSION WITHOUT PARALLEL PROCESS (AVOID MEMORY ERROR)
    logging.info(f'Applying regular expression from {os.path.basename(args.regex)} and sorting peptide aminoacids alphabetically')
    df_processed = subProcessFuncRegex(df_processed, name_col_index, regex_sep, aa_sep, config_regex)

    '''
    # Split dataframe so that each one is processed by one core
    df_split = np.array_split(df_processed, n_cores)

    # Create list of tuples. Each tuple contains arguments received by subProcessFunction
    subprocess_args = [(df_i, name_col_index, regex_sep, aa_sep, config_regex) for df_i in df_split]

    with Pool(n_cores) as p: 
        # logging.info(f'Applying regular expression from {os.path.basename(args.regex)} and sorting peptide aminoacids alphabetically')
        
        # User may send regular expressions, so we must handle possible errors
        try:
            result = p.starmap(subProcessFuncRegex, subprocess_args)
        
        except:
            logging.info('Error when applying regular expressions')
            
            # Log error class and message
            exctype, value = sys.exc_info()[:2]
            log_str = f'{exctype}: {value}'
            logging.info(log_str)

            sys.exit(23) # Status code for Regular expressions

        df_processed = pd.concat(result)
    '''

    # Synonym substitution after to parsing
    logging.info(f'Synonyms substitution after parsing')
    df_processed = synonymsSubstitution(df_processed, name_col_index, synonyms_dict, regex_sep, n_cores)

    # Fuse rows with the same value for the selected columns. Make a fusion before goslin lipid processing to make the code faster
    logging.info(f'Collapsing rows after metabolite name parsing')
    df_processed = fuseTable(df_processed, name_col_index)

    # For each peptide, take only the original part
    logging.info(f'Peptides post-processing (replace alphabetically sorted name by one of the original names)')
    df_processed = originalPeptides(df_processed, name_col_index)

    # Fuse stereoisomers using InChIKey
    df_processed = fuseByInChIKey(df_processed, name_col_index)

    # Write output dataframe
    writeDataFrame(df_processed, args.outdir)

    

if __name__ == '__main__':
    
    # multiprocessing.freeze_support()

    # parse arguments
    parser = argparse.ArgumentParser(
        description='Mod',
        epilog='''
        Example:
            python Mod.py
        
        '''
    )

    # Set default values

    default_config_regex = os.path.join(os.path.dirname(__file__), '..', 'config' , 'configREname', 'regex.ini')
    default_config_parameters = os.path.join(os.path.dirname(__file__), '..', 'config' , 'configREname', 'configREname.ini')
    default_config_synonyms = os.path.join(os.path.dirname(__file__), '..', 'Data' , 'synonyms.json')
    default_lipid_list = os.path.join(os.path.dirname(__file__), '..', 'Data', 'goslinLipidList.csv')

    default_column_index = 5    # Column containing compound names (0-based)
    default_header_index = 0    # Row at which table begins (0-based)
    default_compare_column = "Experimental mass, Name" # Columns used to compare rows during fusion
    default_conserve_column = "Identifier"   # Columns whose value is conserved during fusion
    default_tag_column = "Food, Drug, NaturalProduct, Microbial, Halogenated, Peptide"


    # Parse arguments corresponding to input, .ini and lipid list paths
    parser.add_argument('-i', '--infile', help='Path to input file', required=True, type=str)
    parser.add_argument('-re', '--regex', help='Path to custom regex.ini file', default=default_config_regex, type=str)
    parser.add_argument('-pr', '--param', help='Path to custom parameters.ini file', default=default_config_parameters, type=str)
    parser.add_argument('-js', '--synonyms', help='Path to custom synonyms.json file', default=default_config_synonyms, type=str)
    parser.add_argument('-ll', '--liplist', help='Path to goslin lipid list csv file', default=default_lipid_list, type=str)
    parser.add_argument('-cpu', '--cpuCount', help='Number of cores used in the processing', default=1, type=int)

    # Parameters corresponding to parameters.ini  (not all of them are in parameters.ini file)
    parser.add_argument('-n', '--name', help='Name of output table', type=str)
    parser.add_argument('-od', '--outdir', help="Path to output dir", type=str, default=Path('.'))
    parser.add_argument('-p', '--column', help='Column index of compound names (0-based)', default=default_column_index, type=int)
    parser.add_argument('-r', '--row', help='Row of column headers, at which the table starts (0-based)', default=default_header_index, type=int)
    parser.add_argument('-s', '--separator', help='Characters used to separate compound within a field (accept regex)', type=str)
    parser.add_argument('-aas', '--aa_separator', help='Characters used to separate aminoacids in peptides', type=str)
    parser.add_argument('-rm', '--rmRow', help='Regular expression used in Name field to identify rows that will be dropped', type=str)
    parser.add_argument('-cmp', '--compareCol', help='Index/Name of columns (0-based) that will be compared to make the row fusion (e.g. 0,5)',\
        default=default_compare_column, type=str)
    parser.add_argument('-cns', '--conserveCol', help='Index/Name of columns (0-based) whose values will be conserved during the row fusion (e.g. 1)',\
        default=default_conserve_column, type=str)
    parser.add_argument('-tag', '--tagCol', help='Name of columns containing tags of the compounds (e.g. FoodTag, DrugTag). Their values will be conserved',\
        default=default_tag_column, type=str)
    parser.add_argument('-oc', '--outCol', help='Index/Name of columns present in output table. By default, all columns will be displayed (e.g. 0,2,5)', type=str)

    parser.add_argument('-v', dest='verbose', action='store_true', help='Increase output verbosity')
    args = parser.parse_args()


    # parse config with regular expressions
    config_regex = configparser.ConfigParser(inline_comment_prefixes='#')
    config_regex.read(Path(args.regex))

    # parse config with parameters
    config_param = configparser.ConfigParser(inline_comment_prefixes='#')
    config_param.read(Path(args.param))

    # Parameters introduced in the execution replace those in the .ini file
    if args.name is not None:
        config_param.set('Parameters', 'OutputName', str(args.name))

    if args.separator is not None:
        config_param.set('Parameters', 'Separator', str(args.separator))

    if args.aa_separator is not None:
        config_param.set('Parameters', 'AminoAcidSeparator', str(args.aa_separator))

    if args.rmRow is not None:
        config_param.set('Parameters', 'RemoveRow', str(args.rmRow))

    if args.outCol is not None:
        config_param.set('Parameters', 'OutputColumns', str(args.outCol))


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