#!/bin/bash

# Author: Rafael Barrero Rodriguez
# Date: 2020-11-23
# Description: Script to generate drug_database.tsv and food_database.tsv
# with all synonyms (for now) hmdb database

# Usage example: bash dbs_generator.sh 


SRC_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
HMDB_FILE=$1

# get pre_hmdb_drug.tsv
echo "** Extracting drug"
bash "$SRC_HOME/scripts/hmdb_drug_extractor.sh" $HMDB_FILE

# get pre_hmdb_food.tsv
echo "** Extracting food"
bash "$SRC_HOME/scripts/hmdb_food_extractor.sh" $HMDB_FILE

# get pre_diterpenoids.tsv
echo "** Extracting diterpenoids"
bash "$SRC_HOME/scripts/hmdb_diterpenoids_extractor.sh" $HMDB_FILE

# concatenate pre_hmdb_food.tsv and pre_diterpenoids.tsv
cat "$SRC_HOME/scripts/pre_hmdb_food.tsv" "$SRC_HOME/scripts/pre_hmdb_diterpenoids.tsv" > "$SRC_HOME/scripts/pre_hmdb_food_diterpenoids.tsv"
rm -f "$SRC_HOME/scripts/pre_hmdb_food.tsv" "$SRC_HOME/scripts/pre_hmdb_diterpenoids.tsv"

# get pre_hmdb_drug.tsv synonyms
echo "** Getting drug synonyms"
python "$SRC_HOME/scripts/getAllSynonyms.py" "$SRC_HOME/scripts/pre_hmdb_drug.tsv"
rm -f "$SRC_HOME/drug_database.tsv"
mv "$SRC_HOME/scripts/allSynonyms.tsv" "$SRC_HOME/drug_database.tsv"

# get pre_hmdb_food_diterpenoids.tsv synonyms
echo "** Getting food synonyms"
python "$SRC_HOME/scripts/getAllSynonyms.py" "$SRC_HOME/scripts/pre_hmdb_food_diterpenoids.tsv"
rm -f "$SRC_HOME/food_database.tsv"
mv "$SRC_HOME/scripts/allSynonyms.tsv" "$SRC_HOME/food_database.tsv"