## desktopApp

The desktopApp folder contains the *package.json* and *package-lock.json* files, which allow you to install the Node.js packages and dependencies required for the development and execution of the desktop application. For more information, see [npm-install | npm Docs (npmjs.com)](https://docs.npmjs.com/cli/v6/commands/npm-install).

The *TurboPutative.bat* and *TurboPutative.sh* files allow the application to run on Windows and Linux, respectively. 

The **install** folder contains the *install_win32.bat* and *install_linux.sh* files, which allow you to create a virtual Python environment from which the application's .py modules will be run. For more information, see [12. Virtual Environments and Packages - Python 3.6.12 documentation](https://docs.python.org/3.6/tutorial/venv.html).

The **app** folder contains the application that will run with **Electron** using the precompiled binaries (see *Manual distribution* in [Application Distribution | Electron (electronjs.org)](https://www.electronjs.org/docs/tutorial/application-distribution)).