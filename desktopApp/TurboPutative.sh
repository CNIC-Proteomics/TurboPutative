#!/usr/bin/env bash

# Get script current directory
SRC_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Check if virtual environment is created
if ! [ -f "$SRC_HOME/env/log.info" ]
then
    bash "$SRC_HOME/install/install_linux.sh"
fi

# Electron path
ELECTRON="$SRC_HOME/electron-v11.0.3-linux-x64/electron"

# Enable execution of Electron
chmod u+x "$ELECTRON"

# Execute electron with app
"$ELECTRON" "$SRC_HOME/app"

# If user closed before finishing process, kill processes
if [ $? -eq 99 ]
then
    kill -9 $(ps -o pid= | grep -v -E "($$|$PPID)" ) > /dev/null 2>&1
fi