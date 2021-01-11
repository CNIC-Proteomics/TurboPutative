#!/usr/bin/env bash


###################
# Local functions #
###################

function checkPython {
    "$PYTHON" --version > /dev/null 2>&1

    if [ $? -eq 0 ]
    then
        # if python is in path, check version
        local PY_VERSION="$("$PYTHON" --version)"
        checkVersion "$PY_VERSION"

    else
        # if python is not in path, ask user to give it
        getPython
    fi
}


function checkVersion {
    # get version 
    local VERSION=$(grep -E -o "Python\s[0-9]" <(echo "$1"))
    local SUB_VERSION=$(grep -E -o "Python\s[0-9]\.[0-9]" <(echo "$1") | grep -E -o "[0-9]$")

    if [ "$VERSION" != "Python 3" ]
    then
        echo "** ERROR: Using $VERSION instead of Python 3"
        getPython
    fi

    if ! [ "$SUB_VERSION" -ge "6" ]
    then
        echo "** ERROR: Using $VERSION.$SUB_VERSION instead of Python 3.6 or greater"
        getPython
    fi
    
    createVENV

}


function getPython {
    echo "** Python not found"
    read -p "** Enter full path to Python (or q to exit): " PYTHON
    
    if [ $PYTHON == "q" ]
    then
        endInstall

    else
        checkPython
    fi
}


function createVENV {

    echo "** Creating virtual environment"
    rm -rf "$SRC_HOME/../env"
    "$PYTHON" -m venv "$SRC_HOME/../env"

    if ! [ $? -eq 0 ]
    then
        echo "** ERROR: An error occurred while creating virtual environment"
        rm -rf "$SRC_HOME/../env"
        endInstall
    fi

    local PYTHON_ENV="$SRC_HOME/../env/bin/python"
    local PIP_ENV="$SRC_HOME/../env/bin/pip"

    echo "** Updating pip"
    "$PYTHON_ENV" -m pip install --upgrade pip

    if ! [ $? -eq 0 ]
    then
        echo "** ERROR: An error occurred while updating pip"
        rm -rf "$SRC_HOME/../env"
        endInstall
    fi

    echo "** Installing modules"
    "$PIP_ENV" install numpy pandas xlrd xlwt openpyxl cython --no-warn-script-location
    if ! [ $? -eq 0 ]
    then
        echo "** ERROR: An error occurred while installing modules"
        rm -rf "$SRC_HOME/../env"
        endInstall
    fi

    echo "$(date) - INFO: Python Virtual Environment for TurboPutative created" > "$SRC_HOME/../env/log.info"
    checkVENV
}


function checkVENV {

    if [ -f "$SRC_HOME/../env/log.info" ]
    then
    # if it exists, exit...
        envCreated
    fi

}


function envCreated {
    echo "** Python virtual environment created"
    EXIT_CODE=0
    endInstall
}


function endInstall {
    echo "** Installation process finished"
    exit $EXIT_CODE
}

##############
# Start main #
##############

echo "**"
echo "** CREATING PYTHON VIRTUAL ENVIRONMENT"
echo "**"

# Define SRC_HOME
SRC_HOME="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Default python
PYTHON="python"

# Default exit code
EXIT_CODE=1

# Check if env folder already exists
checkVENV

# Start checking default python
checkPython