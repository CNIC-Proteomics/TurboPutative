#!/bin/bash

WORKFLOW="$1"
INFILE="$2"
JOB_DIR="$3"
JOB_ID="$4"
FEATURE_INFO_INFILE="$5"

# Used for error handling
INFILE_BASENAME="$(basename $INFILE)"
LOG_ERROR="$JOB_DIR/log_error.json"

WF_LEN=$(expr ${#WORKFLOW} - 1)


for MOD_I in $(seq 0 $WF_LEN)
do
    MOD_NUM=${WORKFLOW:MOD_I:1}

    if [ $MOD_NUM == '1' ]
    then
        python "$PWD/src/Tools/pyModules/Tagger.py" -i "$INFILE" -c "$JOB_DIR/Tagger.ini" -od "$JOB_DIR"
        
        # Handle errors
        STATUS_CODE=$?
        
        if ! [ $STATUS_CODE -eq 0 ]; then
            echo "$STATUS_CODE" > "$LOG_ERROR"
            exit 5
        fi

        INFILE="$JOB_DIR/$(cat "$JOB_DIR/Tagger.ini" | awk -F ' = ' '/^OutputName = / {print $2}')"
        
    fi

    if [ $MOD_NUM == '2' ]
    then
        python "$PWD/src/Tools/pyModules/REname.py" -i "$INFILE" -pr "$JOB_DIR/REname.ini"  -od "$JOB_DIR" -re "$JOB_DIR/regex.ini"

        # Handle errors
        STATUS_CODE=$?
        
        if ! [ $STATUS_CODE -eq 0 ]; then
            echo "$STATUS_CODE" > "$LOG_ERROR"
            exit 5
        fi

        INFILE=$JOB_DIR/$(cat $JOB_DIR/REname.ini | awk -F ' = ' '/^OutputName = / {print $2}')
    
    fi

    if [ $MOD_NUM == '3' ]
    then
        python "$PWD/src/Tools/pyModules/RowMerger.py" -i "$INFILE" -c "$JOB_DIR/RowMerger.ini" -od "$JOB_DIR"

        # Handle errors
        STATUS_CODE=$?
        
        if ! [ $STATUS_CODE -eq 0 ]; then
            echo "$STATUS_CODE" > "$LOG_ERROR"
            exit 5
        fi

        INFILE="$JOB_DIR/$(cat "$JOB_DIR/RowMerger.ini" | awk -F ' = ' '/^OutputName = / {print $2}')"
    fi

    if [ $MOD_NUM == '4' ]
    then
        python "$PWD/src/Tools/pyModules/TableMerger.py" -id "$INFILE" -c "$JOB_DIR/TableMerger.ini" -if "$FEATURE_INFO_INFILE" -od "$JOB_DIR"

        # Handle errors
        STATUS_CODE=$?
        FEATINFO_BASENAME="$(basename "$FEATURE_INFO_INFILE")"
        
        if ! [ $STATUS_CODE -eq 0 ]; then
            echo "$STATUS_CODE" > "$LOG_ERROR"
            exit 5
        fi

        INFILE="$JOB_DIR/$(cat "$JOB_DIR/TableMerger.ini" | awk -F ' = ' '/^OutputName = / {print $2}')"
    fi

done

INIT_PATH="$PWD"
cd "$JOB_DIR"
rm *.ini *_log.txt
zip TurboPutativeResults.zip ./*
cd "$INIT_PATH"
#mv $JOB_ID.zip $JOB_DIR/TurboPutativeResults.zip