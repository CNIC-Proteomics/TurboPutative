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
import decimal

import pdb


###################
# Local functions #
###################

class NoNameColumn(Exception):
    pass

class NoMassColumn(Exception):
    pass

class IncorrectNumberOfColumns(Exception):
    pass

class StringToFloat(Exception):
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


def readInfile(infile, row, feature_mass_name, file_type):
    '''
    Input:
        - infile: Path where the file is located
        - row: Index (0-based) of column headers, where the table starts
        - feature_mass_name
        - file_type: Integer. 1 --> Identifications; 2 --> Additional information
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
        
        # Column header is in 1st or 2nd row? Assert it by  mass column name
        while all([not (name in df.columns) for name in feature_mass_name]) and (row+1 < 2):
            row += 1
            df = openFile(infile, row)
        
        # If header is not the n first rows...
        if all([not (name in df.columns) for name in feature_mass_name]):

            # if it is file with identifications, nothing can be done...
            if file_type == 1:
                raise NoMassColumn(f"ERROR: None of the '{feature_mass_name}' possible column names was found")

            # if it is file with additional information, try considering no header...
            if file_type == 2:
        
                # Read complete dataframe assuming that there is no header
                df = openFile(infile, None)

                # Assert that there are 3 columns...
                if df.shape[1] != 3:
                    raise IncorrectNumberOfColumns(f"ERROR: File with additional information must have 3 columns. It has {df.shape[1]} columns")

                # Convert/Assert second column (containing m/z) to float64, handling the possible error
                try:
                    df.iloc[:, 1] = df.iloc[:, 1].astype('float64')

                except:
                    # Log error class and message
                    exctype, value = sys.exc_info()[:2]
                    raise StringToFloat(f"ERROR: {value}")

                # Set column names
                df.columns = ['Feature', 'Experimental mass', 'RT [min]']


        if (file_type == 1) and ('Name' not in df.columns):
            raise NoNameColumn(f"ERROR: Column containing compound names ('Name') was not found")
        
        # Make sure that all column names are string
        df.rename(columns={name: str(name) for name in df.columns}, inplace=True)
    
    except NoNameColumn:
        log_str = f'Error when reading {str(Path(infile))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'NoNameColumn: {value}'
        logging.info(log_str)

        sys.exit(413)
    
    except NoMassColumn:
        log_str = f'Error when reading {str(Path(infile))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'NoNameColumn: {value}'
        logging.info(log_str)
    
        # Status code for column name error
        sys.exit(411) if file_type == 1 else sys.exit(412)

    except IncorrectNumberOfColumns:
        log_str = f'Error when reading {str(Path(infile))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'IncorrectNumberOfColumns: {value}'
        logging.info(log_str)

        sys.exit(414)

    except StringToFloat:
        log_str = f'Error when reading {str(Path(infile))}'
        logging.info(log_str)

        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'StringToFloat: {value}'
        logging.info(log_str)
        
        sys.exit(415)
        
    
    except:
        log_str = f'Error when reading {str(Path(infile))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'{exctype}: {value}'
        logging.info(log_str)

        
        # Status code for column name error
        sys.exit(401) if file_type == 1 else sys.exit(402)
    
    log_str = f'{str(Path(infile))} was read'
    logging.info(log_str)

    return df


def isRT(feature_columns, identification_columns):
    """
    Input:
        - feature_columns: Pandas series containing feature_table columns
        - identification_columns: Pandas series containing identification_table columns
    Output:
        - Boolean: True if both contain RT [min]. Otherwise, False
        - String 1: String with name of RT column in feature table
        - String 2: String with name of RT column in identification table
    """
    rt_regex = re.compile(r'(?i)^(rt|retention time)(\s?\[min\])?$')

    # Loop to search RT [min] in feature columns
    for col in feature_columns:
        feature_regex = rt_regex.search(col)
        if feature_regex: break
    
    # Loop to search RT [min] in identification columns
    for col in identification_columns:
        identification_regex = rt_regex.search(col)
        if identification_regex: break
    
    if feature_regex and identification_regex:
        return True, feature_regex.group(), identification_regex.group()
    
    else: 
        return False, None, None


def rounder(number, n_places, rounding_type):
    '''
    Input:
        - number: floating number
        - n_places: Integer indicating number of decimal places
    Output:
        - res: Float rounded number

    Example: 1516.82825 --> 15168282.5 --> 15168283 --> 1516.8283
    '''
    
    joker = decimal.Decimal(10**n_places)
    res = (decimal.Decimal(str(float(number))) * joker).to_integral_value(rounding=rounding_type)
    res = res / joker
    
    return float(res)


def massRestore(row, original_table, n_digits):
    '''
    Input:
        - row: Pandas series to be restored
        - original_table: Pandas dataframe from which original mass will be taken
        - n_digits: Number of decimal places to which it was rounded
    Output:
        - Pandas series with mass restored
    '''

    # bool array with true where mass match after round
    MZcol_bool = row['Experimental mass'] == original_table.loc[:, 'Experimental mass'].apply(rounder, args=(n_digits, 'ROUND_HALF_UP'))
    
    # bool array with true where rest of the columns match
    all_cols_bool = [row[col] == original_table.loc[:, col] for col in original_table.columns if col != 'Experimental mass']
    all_cols_bool.append(MZcol_bool)

    # bool array corresponding to row where all columns match
    all_cols_bool = [all([col[i] for col in all_cols_bool]) for i in range(len(MZcol_bool))]

    # If only one row match at all, restore original mass
    if sum(all_cols_bool) == 1:
        row['Experimental mass'] = float(original_table.loc[all_cols_bool, 'Experimental mass'])

    return row


def isRow(present_row, new_row):
    '''
    Input:
        - present_row: Pandas series corresponding to merged_table
        - new_row: Dictionary with key corresponding to columns and value of candidate row
    Output:
        - boolean: True if new_row values equals present_row. Otherwise, False
    '''

    return all([new_row[key][0] == present_row[key] if str(present_row[key]) != "nan" else str(new_row[key][0]) == "nan" for key in new_row])
    


def updateTable(merged_table, identification_table_unmatched_restored, feature_row, bool_list, round_value):
    '''
    Input:
        - merged_table: Pandas dataframe with cummulated rematched rows
        - identification_table_unmatched_restored: Pandas dataframe corresponding to identification table. It only contains the rows
          that did not match (original experimental mass)
        - feature_row: Pandas series corresponding to a non-matched row of feature table (original mass)
        - bool_list: List of bools with True in positions of identification_table_unmatched_restored that match to feature_row
        - round_value: Float with the value for experimental mass at which feature_row and identification rows match
    Output:
        - merged_table: Pandas dataframe with new rows added
    '''

    feature_column_names = feature_row.axes[0].to_list()
    identification_column_names = [col for col in identification_table_unmatched_restored.columns if col != 'Experimental mass']

    for index in np.where(bool_list)[0]:
        # get row from identification table
        ident_row = identification_table_unmatched_restored.iloc[index, :]

        # build new row
        new_row = {}
        _ = [new_row.update({col: [feature_row[col]]}) for col in feature_column_names]
        _ = [new_row.update({col: [ident_row[col]]}) for col in identification_column_names]
        new_row['Experimental mass'] = [round_value]

        if not any(merged_table.apply(isRow, axis=1, args=(new_row,), result_type="reduce")):
            # Join if every element in any is False. Any return a False which is converted to True
            # If every element is False in any, then new_row is not contained in merged_table.
            merged_table = pd.concat([merged_table, pd.DataFrame(new_row)])

    return merged_table
        
        

def greedyMergeRow(feature_row, identification_table_unmatched_restored, n_digits, merged_table, use_RT):
    '''
    Input:
        - feature_row: Pandas series corresponding to an unmatched feature row
        - identification_table_unmatched_restored: Pandas dataframe with non-matched rows of identification table (origina mass)
        - n_digits: Integer corresponding to decimal position to round
        - merged_table: Pandas dataframe with cumulated rematched rows
        - use_RT: bool with True if using RT in merge
    Output: 
        - merged_table: Pandas dataframe with new rematched rows. If feature table did not match to identification row, it means
          that its identification row was removed in Mod (non putative annotation). UNK is added to the name in that case.
    '''
    
    # Get column names from each table
    feature_column_names = feature_row.axes[0].to_list()
    identification_column_names = [col for col in identification_table_unmatched_restored.columns if col != 'Experimental mass']

    # Arrays with identification mz rounded up and down
    iden_mz_up = identification_table_unmatched_restored.loc[:, 'Experimental mass'].apply(rounder, args=(n_digits, 'ROUND_HALF_UP'))
    iden_mz_down = identification_table_unmatched_restored.loc[:, 'Experimental mass'].apply(rounder, args=(n_digits, 'ROUND_HALF_DOWN'))

    # Round in different ways
    round_up = rounder(feature_row['Experimental mass'], n_digits, 'ROUND_HALF_UP')
    round_down = rounder(feature_row['Experimental mass'], n_digits, 'ROUND_HALF_DOWN')
    
    # Compare mz
    # bool_up_up = (round_up == iden_mz_up).to_list()  # It is done by default in the first merge
    bool_down_up = (round_down == iden_mz_up).to_list()
    bool_up_down = (round_up == iden_mz_down).to_list()
    bool_down_down = (round_down == iden_mz_down).to_list()
    all_bools = (bool_down_up + bool_up_down + bool_down_down)

    # If using RT during merge
    if use_RT:
        # Get boolean vectors with true where RT are equal
        bool_RT = (feature_row['RT [min]'] == identification_table_unmatched_restored.loc[:, 'RT [min]']).to_list
        
        # Restore boolean vectors, considering RT information
        bool_down_up = list(np.logical_and(bool_down_up, bool_RT))
        bool_up_down = list(np.logical_and(bool_up_down, bool_RT))
        bool_down_down = list(np.logical_and(bool_down_down, bool_RT))

    # Create rows
    # if any(bool_up_up):
    #     merged_table = updateTable(merged_table, identification_table_unmatched_restored, feature_row, bool_up_up, round_up)

    if any(bool_down_up):
        merged_table = updateTable(merged_table, identification_table_unmatched_restored, feature_row, bool_down_up, round_down)

    if any(bool_up_down):
        merged_table = updateTable(merged_table, identification_table_unmatched_restored, feature_row, bool_up_down, round_up)

    if any(bool_down_down):
        merged_table = updateTable(merged_table, identification_table_unmatched_restored, feature_row, bool_down_down, round_down)

    if all([not i for i in all_bools]):
        # If all elems are False (converted to True), its corresponding identification row was removed in Mod (non putative annotation)
        # Add UNK to the name in that case
        new_row = {'Name': ['UNK']}
        _ = [new_row.update({col: [feature_row[col]]}) for col in feature_column_names]
        _ = [new_row.update({col: [""]}) for col in identification_column_names if col not in ['Name', 'Experimental mass']]

        # merged_table.append(new_row, ignore_index=True)
        merged_table = pd.concat([merged_table, pd.DataFrame(new_row)])

    return merged_table


def greedyMerge(feature_table_unmatched_restored, identification_table_unmatched_restored, n_digits, use_RT):
    '''
    Input:
        - feature_table_unmatched_restored: Pandas dataframe with non-matched rows of feature table
        - identification_table_unmatched_restored: Pandas dataframe with non-matched rows of identification table
        - n_digits: Integer corresponding to rounded decimal place
        - use_RT: bool with True if using RT in merge
    Output:
        - merged_table: Pandas dataframe with table of non-matched rows (sub-merge)
    '''
    
    # Get column names from each table
    feature_column_names = feature_table_unmatched_restored.columns.to_list()
    identification_column_names = [col for col in identification_table_unmatched_restored.columns if col != 'Experimental mass']

    # Merge table to which new rows will be added
    all_column_names = feature_column_names + identification_column_names
    merged_table = pd.DataFrame({col: [] for col in all_column_names})

    # Loop over each non-matched row of feature table
    # Each row generate a pandas dataframe that we must concatenate
    for i in range(len(feature_table_unmatched_restored)):
        merged_table = greedyMergeRow(feature_table_unmatched_restored.iloc[i, :], identification_table_unmatched_restored, \
            n_digits, merged_table, use_RT)

    # Unmatched rows from identification table may still be unmatched
    # Find those rows that still are unmatched
    identification_name_bool = [True if sum(merged_table['Name'].str.contains(name, regex=False)) == 0 else False \
                                    for name in identification_table_unmatched_restored['Name'].to_list() \
                                ]
    # Create another merged dataframe. Rows are got from unmatched identification table and adding NA to columns of FeatureInfo
    merged_table_ident_unmatch = pd.DataFrame(identification_table_unmatched_restored.loc[identification_name_bool, :].apply(
        lambda row: {col: row[col] if col in row.index else "NA" for col in all_column_names}, axis=1, result_type='expand'))

    # Merge both tables
    merged_table = pd.concat([merged_table, merged_table_ident_unmatch])    

    return merged_table



def reMatch(feature_table_original, identification_table_original, merged_table, n_digits, feature_table, identification_table, use_RT):
    '''
    Input:
        - feature_table_original: Pandas dataframe with original feature info table
        - identification_table_original: Pandas dataframe with original identification table
        - merged_table: Pandas dataframe obtained in merged (outer product) between featureInfo and identification tables
        - n_digits: Integer with  decimal position to round
        - feature_table: Pandas dataframe with feature info table (experimental mass rounded)
        - identification_table: Pandas dataframe with identification table (experimental mass rounded)
        - use_RT: bool with True if using RT in merge
    Output:
        - merged_table: Pandas dataframe with final merge
    '''

    # Get unmatched rows of feature table
    feature_table_unmatched = merged_table.loc[merged_table.loc[:, 'Name'].apply(lambda name: str(name) == 'nan'), feature_table_original.columns]
    feature_table_unmatched_restored = feature_table_unmatched.apply(massRestore, axis=1, args=(feature_table_original, n_digits))

    # Get unmatched rows of identification table
    identification_table_unmatched = merged_table.loc[merged_table.apply(
        lambda row: all([str(row[col]) == 'nan' for col in feature_table_original.columns if col != 'Experimental mass']),
        axis=1), identification_table_original.columns]

    identification_table_unmatched_restored = identification_table_unmatched.apply(massRestore, axis=1, args=(identification_table_original, n_digits))

    # Greedy ReMerge with unmatch rows
    if len(feature_table_unmatched_restored) > 0 and len(identification_table_unmatched_restored) > 0:
        sub_merged_unmatch = greedyMerge(feature_table_unmatched_restored, identification_table_unmatched_restored, n_digits, use_RT)
        sub_merged_match = pd.merge(feature_table, identification_table, how = 'inner', on = 'Experimental mass') if not use_RT \
            else pd.merge(feature_table, identification_table, how = 'inner', on = ['Experimental mass', 'RT [min]'])
        merged_table = pd.concat([sub_merged_match, sub_merged_unmatch])

    return merged_table


def mergeTable(feature_table, identification_table, feature_mass_name, use_RT):
    '''
    Input:
        - feature_table: Pandas dataframe containing feature ID, Apex m/z and RT
        - identification_table: Pandas dataframe containing identifications
        - feature_mass_name: List of string with the accepted names for the column containing feature mass
        - use_RT: bool with True if using RT in merge
    
    Output:
        - merged_table: Pandas dataframe obtained from merging feature_table and identification_table
    '''

    # Accepted names for the column containing feature mass
    # feature_mass_name = ['Apex m/z', 'Experimental mass', 'mz', 'm/z', 'MZ', 'M/Z', 'Mz', 'mZ']

    # Is the name in feature_table?
    feature_table_bool = [name in feature_table.columns for name in feature_mass_name]

    # Is the name in identification_table?
    identification_table_bool = [name in identification_table.columns for name in feature_mass_name]

    # Assert that column names are correct
    assert feature_table_bool,\
        f"Name of the column with feature mass should be one of the following in the list: {feature_mass_name}"
    
    assert identification_table_bool,\
        f"Name of the column with feature mass should be one of the following in the list: {feature_mass_name}"
    
    
    # Get number of digits to round numbers
    n_digits = config_param.getint('Parameters', 'N_Digits')

    # Rename table column: Apex m/z --> Experimental mass
    feature_table.columns = [name if name not in feature_mass_name else "Experimental mass" for name in feature_table.columns]

    identification_table.columns = [name if name not in feature_mass_name else "Experimental mass" for name in identification_table.columns]

    # Maintain original
    feature_table_original = feature_table.copy()
    identification_table_original = identification_table.copy()

    # Round numbers in both dataframes
    feature_table.loc[:, 'Experimental mass'] = feature_table.loc[:, 'Experimental mass'].apply(rounder, args=(n_digits, 'ROUND_HALF_UP'))
    identification_table.loc[:, 'Experimental mass'] = identification_table.loc[:, 'Experimental mass'].apply(rounder, args=(n_digits, 'ROUND_HALF_UP'))

    # Merge both tables
    merged_table = pd.merge(feature_table, identification_table, how = 'outer', on = 'Experimental mass') if not use_RT \
        else pd.merge(feature_table, identification_table, how = 'outer', on = ['Experimental mass', 'RT [min]'])

    # Non matched rows can be caused by wrong round or removal of identifications in Mod
    merged_table = reMatch(feature_table_original, identification_table_original, merged_table, n_digits, feature_table, identification_table, use_RT)

    return merged_table
        

def getOutputFilename():
    '''
    Output:
        - filename: String containing the name of the output file
    '''

    filename = config_param.get('Parameters', 'OutputName')
    filename = os.path.splitext(filename)[0] + '.xlsx'
    
    if not filename:
        filename = 'Tmerged_' + os.path.basename(args.identification)

    if not os.path.splitext(filename)[1]:
        filename += '.xlsx'
    
    return filename


def writeDataFrame(df, path):
    '''
    Description: Function used to export pandas dataframe with the tags added

    Input:
        - df: Pandas dataframe that will be exported
        - path: String containing the path to infile. The new file will be saved in the
        same folder.
    '''

    # Build output file path
    output_path = path
    
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
    
    # Get output file name
    filename = getOutputFilename()

    output_file = os.path.join(output_path, filename)

    # Get output columns
    if config_param.get('Parameters', 'OutputColumns'):
        output_columns = [name.strip() for name in config_param.get('Parameters', 'OutputColumns').split(',') if name.strip() in df.columns]
    
    else:
        output_columns = df.columns

    # Handle errors in exception case
    try:
        df.to_excel(output_file, index=False, columns=output_columns)
    
    except:
        log_str = f'Error when writing {str(Path(output_file))}'
        logging.info(log_str)
        
        # Log error class and message
        exctype, value = sys.exc_info()[:2]
        log_str = f'{exctype}: {value}'
        logging.info(log_str)

        sys.exit()
    
    log_str = f'Write Output Table: {str(Path(output_file))}'
    logging.info(log_str)



##################
# Main functions #
##################

def main(args):
    '''
    main function
    '''
    
    # Accepted names for the column containing mz values in the input tables
    feature_mass_name = ['Apex m/z', 'Experimental mass', 'mz', 'm/z', 'MZ', 'M/Z', 'Mz', 'mZ']
    
    # Get table with feature information
    feature_table = readInfile(args.feature, 0, feature_mass_name, 2)

    # Get table with identifications
    identification_table = readInfile(args.identification, 0, feature_mass_name, 1)

    # Use retention time in merge (True: Yes, False: No)
    use_RT, feature_RTcol, identification_RTcol = isRT(feature_table.columns, identification_table.columns)
    
    # Change name of RT columns to make them equal in both tables
    if use_RT:
        feature_table.rename(columns={feature_RTcol:'RT [min]'})
        identification_table.rename(columns={identification_RTcol:'RT [min]'})

    # Merge both tables based on experimental mass
    merged_table = mergeTable(feature_table, identification_table, feature_mass_name, use_RT)

    # Export merged table
    writeDataFrame(merged_table, args.outdir)



if __name__=="__main__":
    
    # parse arguments
    parser = argparse.ArgumentParser(
        description='FeatureInfo',
        epilog='''
        Example:
            python FeatureInfo.py
        
        '''
    )

    # Set default values
    default_config_path = os.path.join(os.path.dirname(__file__), '..', 'config' , 'configFeatureInfo', 'configFeatureInfo.ini')

    # Parse arguments corresponding to path files
    parser.add_argument('-if', '--feature', help="Path to input file with feature information", type=str, required=True)
    parser.add_argument('-id', '--identification', help="Path to input file with identifications", type=str, required=True)
    parser.add_argument('-c', '--config', help="Path to configFeatureInfo.ini file", type=str, default=default_config_path)
 
    # Parse arguments corresponding to parameters
    parser.add_argument('-o', '--output', help="Name of output table", type=str)
    parser.add_argument('-od', '--outdir', help="Path to output dir", type=str, default=Path('.'))
    parser.add_argument('-oc', '--outCol', help='Name/Index of columns present in output table. By default, all columns will be displayed', type=str)
    parser.add_argument('-n', '--digits', help="Number of digits", type=str)

    parser.add_argument('-v', dest='verbose', action='store_true', help='Increase output verbosity')
    args = parser.parse_args()


    # parse config with user selection
    config_param = configparser.ConfigParser(inline_comment_prefixes='#')
    config_param.read(Path(args.config))

    # Parameters introduced in the execution replace those in the .ini file

    if args.digits:
        config_param.set('Parameters', 'N_Digits', args.digits)

    if args.output:
        config_param.set('Parameters', 'OutputName', args.output)
    
    if args.outCol:
        config_param.set('Parameters', 'OutputColumns', args.outCol)



    # logging debug level. By default, info level
    if args.identification:
        log_file = outfile = os.path.splitext(args.identification)[0] + '_log.txt'
        log_file_debug = outfile = os.path.splitext(args.identification)[0] + '_log_debug.txt'
    
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