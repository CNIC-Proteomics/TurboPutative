#!/bin/bash

# CURRENT DIRECTORY
SRC_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# PYTHON ENGINE
# PYTHON="$SRC_HOME/python/bin/python3"
PYTHON="python3"
#PYTHON=python

PY_MODULES="$SRC_HOME/pyModules"

# INPUT VARIABLES
WORKFLOW="$1"
INFILE="$2"
JOB_DIR="$3"
FEATURE_INFO_INFILE="$4"


# Used for error handling
INFILE_BASENAME="$(basename $INFILE)"
LOG_ERROR="$JOB_DIR/log_error.json"

# FIRST MESSAGE TO LOG
echo >> "$JOB_DIR/WF.log"
echo Initializing workflow >> "$JOB_DIR/WF.log"

WF_LEN=$(expr ${#WORKFLOW} - 1)

for MOD_I in $(seq 0 $WF_LEN)
do
    MOD_NUM=${WORKFLOW:MOD_I:1}

    if [ $MOD_NUM == '1' ]
    then
        echo Running Tagger >> "$JOB_DIR/WF.log"
        $PYTHON "$PY_MODULES/Tagger.py" -i "$INFILE" -c "$JOB_DIR/Tagger.ini" -od "$JOB_DIR"
        
        # Handle errors
        STATUS_CODE=$?
        
        if ! [ $STATUS_CODE -eq 0 ]; then
            exit $STATUS_CODE
        fi

        INFILE="$JOB_DIR/$(cat "$JOB_DIR/Tagger.ini" | awk -F ' = ' '/^OutputName = / {print $2}')"
        
    fi

    if [ $MOD_NUM == '2' ]
    then
        echo Running REname >> "$JOB_DIR/WF.log"
        $PYTHON "$PY_MODULES/REname.py" -i "$INFILE" -pr "$JOB_DIR/REname.ini"  -od "$JOB_DIR" -re "$JOB_DIR/regex.ini"

        # Handle errors
        STATUS_CODE=$?
        
        if ! [ $STATUS_CODE -eq 0 ]; then
            exit $STATUS_CODE
        fi

        INFILE="$JOB_DIR/$(cat "$JOB_DIR/REname.ini" | awk -F ' = ' '/^OutputName = / {print $2}')"
    
    fi

    if [ $MOD_NUM == '3' ]
    then
        echo Running RowMerger >> "$JOB_DIR/WF.log"
        $PYTHON "$PY_MODULES/RowMerger.py" -i "$INFILE" -c "$JOB_DIR/RowMerger.ini" -od "$JOB_DIR"

        # Handle errors
        STATUS_CODE=$?
        
        if ! [ $STATUS_CODE -eq 0 ]; then
            exit $STATUS_CODE
        fi

        INFILE="$JOB_DIR/$(cat "$JOB_DIR/RowMerger.ini" | awk -F ' = ' '/^OutputName = / {print $2}')"
    fi

    if [ $MOD_NUM == '4' ]
    then
        echo Running TableMerger >> "$JOB_DIR/WF.log"
        $PYTHON "$PY_MODULES/TableMerger.py" -id "$INFILE" -c "$JOB_DIR/TableMerger.ini" -if "$FEATURE_INFO_INFILE" -od "$JOB_DIR"

        # Handle errors
        STATUS_CODE=$?
        FEATINFO_BASENAME="$(basename "$FEATURE_INFO_INFILE")"
        
        if ! [ $STATUS_CODE -eq 0 ]; then
            exit $STATUS_CODE
        fi

        INFILE="$JOB_DIR/$(cat "$JOB_DIR/TableMerger.ini" | awk -F ' = ' '/^OutputName = / {print $2}')"
    fi

done

# Delete log and ini files
rm "$JOB_DIR"/*.ini "$JOB_DIR"/*_log.txt "$JOB_DIR"/WF.log

INIT_PATH="$PWD"
cd "$JOB_DIR"
zip TurboPutativeResults.zip ./*
cd "$INIT_PATH"

exit 0