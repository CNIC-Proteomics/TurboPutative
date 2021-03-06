@ECHO OFF

:: CURRENT DIRECTORY
SET SRC_HOME=%~dp0
SET SRC_HOME=%SRC_HOME:"=%
SET SRC_HOME=%SRC_HOME:~0,-1%

:: PYTHON EXE
REM SET PYTHON="%SRC_HOME%\python\python.3.6.7\tools\python.exe"
SET TAGGER=%SRC_HOME%\pyModules\compiledModules\Tagger\Tagger.exe
SET RENAME=%SRC_HOME%\pyModules\compiledModules\REname\REname.exe
SET ROWMERGER=%SRC_HOME%\pyModules\compiledModules\RowMerger\RowMerger.exe
SET TABLEMERGER=%SRC_HOME%\pyModules\compiledModules\TableMerger\TableMerger.exe

SET FOODLIST=%SRC_HOME%\Data\food_list.tsv
SET DRUGLIST=%SRC_HOME%\Data\drug_list.tsv
SET MICROBIALLIST=%SRC_HOME%\Data\microbial_list.tsv
SET PLANTLIST=%SRC_HOME%\Data\plant_list.tsv
SET NPLIST=%SRC_HOME%\Data\natural_product_list.tsv
SET GOSLINLIST=%SRC_HOME%\Data\goslinLipidList.csv
SET SYNONYMS=%SRC_HOME%\Data\synonyms.json

:: INPUT VARIABLES
SET WORKFLOW=%~1
SET INFILE=%~2
SET JOB_DIR=%~3
SET FEATURE_INFO_INFILE=%~4
SET CPU=%~5

:: FIRST MESSAGE TO LOG
ECHO. >> "%JOB_DIR%\WF.log"
ECHO Initializing workflow >> "%JOB_DIR%\WF.log"


SETLOCAL EnableDelayedExpansion

:moduleIterator
	:: Get the first letter of the workflow
	SET MODULE=%WORKFLOW:~0,1%
	SET WORKFLOW=%WORKFLOW:~1%

	IF %MODULE% == 1 (
	:: Execute Tagger
		ECHO Running Tagger >> "!JOB_DIR!\WF.log"
		CMD /C " "!TAGGER!" -i "!INFILE!" -c "!JOB_DIR!\Tagger.ini" -od "!JOB_DIR!" -cpu %CPU% -fL "!FOODLIST!" -dL "!DRUGLIST!" -mL "!MICROBIALLIST!" -pL "!PLANTLIST!" -npL "!NPLIST!" "
		IF !ERRORLEVEL! NEQ 0 (
			SET ERROR_CODE=!ERRORLEVEL!
			GOTO :EndProcess
		)

		:: Output of this module is input of the next
		FOR /F "useback delims== tokens=1,2" %%i in ("!JOB_DIR!\Tagger.ini") DO IF "%%i" == "OutputName " SET INFILE=%%j
		SET INFILE=!JOB_DIR!\!INFILE:~1!
	)

	IF %MODULE% == 2 (
	:: Execute REname
		ECHO Running REname >> "%JOB_DIR%\WF.log"
		CMD /C " "!RENAME!" -i "!INFILE!" -pr "!JOB_DIR!\REname.ini"  -od "!JOB_DIR!" -re "!JOB_DIR!\regex.ini"  -cpu %CPU% -ll "!GOSLINLIST!" -js "!SYNONYMS!" "
		IF !ERRORLEVEL! NEQ 0 (
			SET ERROR_CODE=!ERRORLEVEL!
			GOTO :EndProcess
		)

		:: Output of this module is input of the next
		FOR /F "useback delims== tokens=1,2" %%i in ("!JOB_DIR!\REname.ini") DO IF "%%i" == "OutputName " SET INFILE=%%j
		SET INFILE=!JOB_DIR!\!INFILE:~1!
	)

	IF %MODULE% == 3 (
	:: Execute RowMerger
		ECHO Running RowMerger >> "!JOB_DIR!\WF.log"
		CMD /C " "!ROWMERGER!" -i "!INFILE!" -c "!JOB_DIR!\rowMerger.ini" -od "!JOB_DIR!" "
		IF !ERRORLEVEL! NEQ 0 (
			SET ERROR_CODE=!ERRORLEVEL!
			GOTO :EndProcess
		)

		:: Output of this module is input of the next
		FOR /F "useback delims== tokens=1,2" %%i in ("!JOB_DIR!\rowMerger.ini") DO IF "%%i" == "OutputName " SET INFILE=%%j
		SET INFILE=!JOB_DIR!\!INFILE:~1!
	)

	IF %MODULE% == 4 (
	:: Execute TableMerger
		ECHO Running TableMerger >> "!JOB_DIR!\WF.log"
		CMD /C " "!TABLEMERGER!" -id "!INFILE!" -c "!JOB_DIR!\tableMerger.ini" -if "!FEATURE_INFO_INFILE!" -od "!JOB_DIR!" "
		IF !ERRORLEVEL! NEQ 0 (
			SET ERROR_CODE=!ERRORLEVEL!
			GOTO :EndProcess
		)

		:: Output of this module is input of the next
		FOR /F "useback delims== tokens=1,2" %%i in ("!JOB_DIR!\tableMerger.ini") DO IF "%%i" == "OutputName " SET INFILE=%%j
		SET INFILE=!JOB_DIR!\!INFILE:~1!
	)

	:: If there is still workflow go to next iteration
	IF defined WORKFLOW ( 
		GOTO :moduleIterator
	)


:EndProcess
	DEL "!JOB_DIR!"\*_log.txt "!JOB_DIR!"\*.ini
	ECHO Finished workflow >> "!JOB_DIR!\WF.log"
	EXIT /B %ERROR_CODE%