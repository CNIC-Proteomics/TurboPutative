# TurboPutative

## Installation Manual

The different releases of the application can be downloaded from GitHub. Thus, the desktop application is available for **Windows** (TurboPutative-x.x.x-win32-x64.zip) and for **Linux** (TurboPutative-x.x.x-linux-x64.zip). In both cases, it will be necessary to have **Python 3.6** or a higher version installed in order to use the application ([Download Python | Python.org](https://www.python.org/downloads/)).

To start using the **Windows** version it is necessary to run the *TurboPutative.bat* file. The first time it is run, the creation of the Python virtual environment will start with the required libraries (Numpy, Pandas, Cython, xlrd, xlwt and openpyxl). If Python is not found in the system PATH (or if Python is not Python 3.6 or higher), the user will be prompted to enter the full address to a valid Python executor. The virtual environment will be created in the env folder of the application root directory. The desktop application can then be started by running TurboPutative.bat.

To use TurboPutative on **Linux** it is necessary to run the *TurboPutative.sh* file from a terminal (or use the Bash interpreter: `bash TurboPutative.sh`). The first time it is run, the Python virtual environment will be created in a similar way to that described for the Windows version. After creating the virtual environment, you can use the desktop application by running TurboPutative.sh.

Finally, it is possible to download the **server source code** at TurboPutative-x.x.x-webServer.zip. To start the web server as *localhost* it is necessary to use Linux and to have Node.js and its npm package manager ([Node.js](https://nodejs.org/en/)) installed on the computer. After unzipping the downloaded .zip file, the `npm install` command must be executed from the root folder and using the terminal, in order to download the required packages and dependencies. To start the server, the command `npm start` must be executed from the root folder of the project and using the terminal. The local server will then listen for connections on port 8080, and requests can be sent by entering http://localhost:8080/ in the browser.

## Source Code Organization

The source code content is organized in three main folders contained in the root directory: **desktopApp**, **webApp** and **tools**. The desktopApp folder contains the files and code for the desktop application on Windows and Linux. The webApp folder contains the files and code for the web application. Finally, the tools folder contains some tools and other files used for TurboPutative development.