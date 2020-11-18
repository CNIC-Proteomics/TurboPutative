#!/bin/bash

# Get script current directory
SRC_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Execute electron with app
"$SRC_HOME/node_modules/electron/dist/electron" "$SRC_HOME/app"