@ECHO OFF

:: Root directory
SET SRC_HOME="%~dp0"
SET SRC_HOME=%SRC_HOME:"=%
SET SRC_HOME=%SRC_HOME:~0,-1%

:: Directory containing .py modules
SET PY_PATH="%SRC_HOME%\app\src\pyModules"

:: Remove and create compiledModules folder
RMDIR /S /Q "%PY_PATH%\compiledModules" > NUL 2>&1
MKDIR "%PY_PATH%\compiledModules"

:: Compile modules
ECHO ** Compile Tagger
pyinstaller -y --distpath "%PY_PATH%\compiledModules" --hidden-import xlrd --hidden-import xlwt --hidden-import openpyxl "%PY_PATH%\Tagger.py"
IF NOT "%ERRORLEVEL%"=="0" GOTO :error


ECHO ** Compile REname
pyinstaller -y --distpath "%PY_PATH%\compiledModules" --hidden-import xlrd --hidden-import xlwt --hidden-import openpyxl --hidden-import cython "%PY_PATH%\REname.py" 

RMDIR /S /Q "%PY_PATH%\compiledModules\REname\pygoslin" > NUL 2>&1
XCOPY /E /I "%PY_PATH%\pygoslin" "%PY_PATH%\compiledModules\REname\pygoslin"


IF NOT "%ERRORLEVEL%"=="0" GOTO :error

ECHO ** Compile RowMerger
pyinstaller -y --distpath "%PY_PATH%\compiledModules" --hidden-import xlrd --hidden-import xlwt --hidden-import openpyxl "%PY_PATH%\RowMerger.py"

IF NOT "%ERRORLEVEL%"=="0" GOTO :error

ECHO ** Compile TableMerger
pyinstaller -y --distpath "%PY_PATH%\compiledModules" --hidden-import xlrd --hidden-import xlwt --hidden-import openpyxl "%PY_PATH%\TableMerger.py"

IF NOT "%ERRORLEVEL%"=="0" GOTO :error

GOTO :EndProcess

:: Error in compilation
:error
ECHO ** An error occurred during compilation
GOTO :EndProcess

:: End compilation
:EndProcess
ECHO ** Compilation process finished
PAUSE