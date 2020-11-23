@ECHO OFF

ECHO **
ECHO ** CREATION OF PYTHON VIRTUAL ENVIRONMENT
ECHO **

:: SET WORKING DIRECTORY
SET SRC_HOME="%~dp0"
SET SRC_HOME=%SRC_HOME:"=%
SET SRC_HOME=%SRC_HOME:~0,-1%

:: SET env FOLDER
SET SRC_ENV=%SRC_HOME%\..\env

SETLOCAL EnableDelayedExpansion

:: CHECK IF env FOLDER EXISTS
:CHECK_ENV
IF EXIST "%SRC_ENV%" (
    
    GOTO ENV_CREATED

) ELSE (

    ECHO ** Check if Python is installed  
    SET PYTHON=py

    WHERE !PYTHON! > NUL 2>&1

    IF ERRORLEVEL 1 (
        ECHO ** !PYTHON! was not found in PATH...
        GOTO USER_PYTHON
    ) ELSE (
        GOTO CREATE_ENV
    )

)


:: USER PYTHON INTRODUCTION
:USER_PYTHON

SET /P PYTHON="** Enter path to python.exe or 'q' to exit installation: "
IF %PYTHON% == q GOTO END
GOTO ASSERT_PYTHON


:: CHECK IF PYTHON IS INSTALLED
:ASSERT_PYTHON

IF EXIST %PYTHON% (

    GOTO CREATE_ENV

) ELSE (

    ECHO ** Python could not be found: %PYTHON%
    GOTO USER_PYTHON

)


:: CREATE VIRTUAL ENVIRONMENT
:CREATE_ENV
ECHO ** Check Python version

FOR /F "useback delims=. tokens=1,2" %%I IN (`%PYTHON% --version`) DO (
    
    IF NOT "%%I" == "Python 3" (
        ECHO ** ERROR: Using %%I instead of Python 3
        GOTO USER_PYTHON
    )

    IF NOT %%J GEQ 6 (
        ECHO ** ERROR: Using %%I.%%J instead of Python 3.6 or greater
        GOTO USER_PYTHON
    )

)

ECHO ** Creating virtual environment
CMD /C " "%PYTHON%" -m venv "%SRC_ENV%" "

IF ERRORLEVEL 1 GOTO END

SET SRC_SCRIPTS=%SRC_ENV%\Scripts

REM UPGRADE PIP
ECHO ** Upgrading pip
CMD /C  " "%SRC_SCRIPTS%\python.exe" -m pip install --upgrade pip "

IF ERRORLEVEL 1 GOTO END

REM INSTALAR NUMPY y PANDAS
ECHO ** Installing modules
CMD /C " "%SRC_SCRIPTS%\pip.exe" install numpy pandas xlrd xlwt "

IF ERRORLEVEL 1 GOTO END

GOTO ENV_CREATED



:ENV_CREATED
ECHO ** Virtual environment created
GOTO END


:END
ECHO ** Installation process finished. Press ENTER to close...
PAUSE