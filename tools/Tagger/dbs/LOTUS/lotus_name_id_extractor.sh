#!/bin/bash

# Name: Rafael Barrero
# Date: 2020-03-03
# Description: Script to extract compound names and coconut id from sdf file.
# Usage example: bash lotus_name_id_extractor.sh

# GLOBAL VARIABLES
FILE="LOTUS_DB_LATEST.sdf"

# EXTRACT COMPOUND NAMES WITH ID
cat $FILE | awk '
    BEGIN {id=""; n=0; i=0; j=0; print "Name\tCOCONUT_ID"}

    /^> <coconut_id>$/ {i=NR+1}
    NR==i {id=$0; i=0}

    /^> <name>$/ {j=NR+1}
    NR==j {n=split($0, nameArr, "; "); j=0}

    /^\$\$\$\$$/ {for(k=1; k<=n; k++) print nameArr[k]"\t"id}
' > lotus_NP.tsv