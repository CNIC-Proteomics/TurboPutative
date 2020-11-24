const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawn, spawnSync, execSync } = require('child_process');
const { finished } = require('stream');

// Global variables
const nCores = Number((os.cpus().length*0.5).toFixed(0)); // Number of cores used

var win; // Windows openned (the only one)
var batch; // Process spawned when running workflow
var killed = false; // Variable used to know if user killed running process

const index = path.join('file://', __dirname, 'index.html');
const moduleSelector = path.join('file://', __dirname, 'sections', 'execute', 'moduleSelector.html');
const infile = path.join('file://', __dirname, 'sections', 'execute', 'infile.html');
const tagger = path.join('file://', __dirname, 'sections', 'execute', 'tagger.html');
const REname = path.join('file://', __dirname, 'sections', 'execute', 'REname.html');
const rowMerger = path.join('file://', __dirname, 'sections', 'execute', 'rowMerger.html');
const tableMerger = path.join('file://', __dirname, 'sections', 'execute', 'tableMerger.html');
const loader = path.join('file://', __dirname, 'sections', 'execute', 'loader.html');
const error = path.join('file://', __dirname, 'sections', 'execute', 'error.html');
const results = path.join('file://', __dirname, 'sections', 'execute', 'results.html');

var modToURL = {'Tagger': tagger, 'REname': REname, 'RowMerger': rowMerger, 'TableMerger': tableMerger, 'infile': infile};
var modToNum = {'Tagger': 1, 'REname': 2, 'RowMerger': 3, 'TableMerger': 4};

const jobsPath = path.join(__dirname, 'jobs'); // Path to results directories

const errorCode = JSON.parse(fs.readFileSync(path.join(__dirname, 'assets', 'files', 'errorCode.json'))); // Create json with error code

// Functions to show different pages
function showMainPage () {

    win = new BrowserWindow({
        width: 780,
        height: 655,
        webPreferences: {
            nodeIntegration: true
        },
        icon: path.join(__dirname, 'assets', 'images', 'icon2.ico')
    })

    // No menu
    win.setMenu(null);
    
    // Load index.html
    win.loadURL(index);

    // win.webContents.openDevTools();
}

// Start app
app.whenReady().then(showMainPage);

// Close app when all windows are closed
app.on('window-all-closed', () => {

    if (batch) {
        // If spawn process has been run...
        
        if (batch.exitCode == null) {
            // if batch.exitCode is null, spawned process is still running. In that case, kill the process

            if (process.platform == "win32") {
                killed = true;
                spawnSync("TASKKILL", ["/F", "/T", "/PID", batch.pid]);
            } else if (process.platform == "linux") {
                app.exit(99)
            }
        }
    }
    
    app.quit();
})

// Event Handling
ipcMain.on('select-modules', (e, workflow) => {
    // Send next window

    // Take next win from workflow object
    var nextWin = workflow.next > -1 ? workflow.modules[workflow.next] : "infile";
    var nextWinPath = modToURL[nextWin];
    
    // Show next window in renderer process
    var loadURL = win.loadURL(nextWinPath);
    
    // When web page is laoded, send workflow object
    loadURL.then((val) => {
        e.reply('send-workflow', workflow);
    });
    
});

ipcMain.on('go-back', (e, workflow) => {
    // User clicked return button

    // Show previous windows
    var previousWin = (workflow.next-2 > -1) ? workflow.modules[workflow.next-2] : "infile";
    var previousWinPath = modToURL[previousWin];
    var loadURL = win.loadURL(previousWinPath);

    // When page is loaded, send workflow object
    loadURL.then((val) => {
        e.reply('send-workflow-from-next', workflow);
    });

});

ipcMain.on('run-workflow', (e, workflow) => {
    // Run workflow and send waiting page

    // console.log(workflow);
    var loadURL = win.loadURL(loader);

    // Define workflow jobID
    workflow.jobID = makeid(10);
    workflowPath = path.join(jobsPath, workflow.jobID);

    // Send workflow object so as loader can ask...
    loadURL.then((val) => {
        e.reply('send-workflow', workflow);
    })

    // Create workflow folder
    fs.mkdirSync(workflowPath);

    // Create log
    fs.writeFileSync(path.join(workflowPath, "WF.log"), "Preparing workflow");

    // Create .ini files
    for (key in workflow.ini) {
        // Define ini path and write it
        iniPath = path.join(workflowPath, `${key}.ini`);
        fs.writeFileSync(iniPath, workflow.ini[key]);
    }
    
    // Define path to files uploaded by user
    infile_user = path.join(workflowPath, workflow.files.infile.name); // Define path where infile user can be found
    infile_feature_info = workflow.modules.includes('TableMerger') ? path.join(workflowPath, workflow.files.featInfo.name) : "" // If selected


    // Move input files to workflow folder
    fs.copyFileSync(workflow.files.infile.path, infile_user); // Main input
    
    if (infile_feature_info != "") fs.copyFileSync(workflow.files.featInfo.path, infile_feature_info); // Input for TableMerger

    if (Object.keys(workflow.files.regex).length > 0) {
        // if user sent regex.ini, use it
        fs.copyFileSync(workflow.files.regex.path, path.join(workflowPath, 'regex.ini'));

    } else {
        // if user did not send regex.ini, use default
        fs.copyFileSync(path.join(__dirname, 'src', 'config', 'configREname', 'regex.ini'), path.join(workflowPath, 'regex.ini'));
    }


    // Write workflow with numerical string
    var modulesString = ""; // Create numeric string
    for (i=0; i<workflow.modules.length; i++) modulesString += modToNum[workflow.modules[i]];

    // Run Bash script
    if (process.platform == 'linux') {
        // If linux...
        runWorkflow('linux', modulesString, infile_user, workflowPath, infile_feature_info, e, workflow);

    } else if (process.platform == 'win32') {
        // if windows...
        runWorkflow('win32', modulesString, infile_user, workflowPath, infile_feature_info, e, workflow);
    }

})

ipcMain.on('see-results', (e, workflow) => {
    // When user clicks to see new results...

    if (process.platform == 'linux') {
        // If linux OS
        var workflowPath = path.join(__dirname, 'jobs', workflow.jobID);

        const bash = spawn('xdg-open', [workflowPath]);

        bash.stdout.on('data', (data) => {
            console.log(`stdout: ${data}`);
        });

        bash.stderr.on(`data`, (data) => {
            console.error(`stdout: ${data}`);
        });

        bash.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
        });

    } else if (process.platform == 'win32') {
        // If win32 OS
        var workflowPath = path.join(__dirname, 'jobs', workflow.jobID);

        exec(`START "" "${workflowPath}" `, (error, stdout, stderr) => {
            if (error) {
            console.error(`exec error: ${error}`);
            return;
            }
            console.log(`stdout: ${stdout}`);
            console.error(`stderr: ${stderr}`);
        });

    }

});

ipcMain.on('workflow-status', (e, workflow) => {
    // When loader asks about workflow status...

    // path to WF.log
    var logFile = path.join(jobsPath, workflow.jobID, "WF.log");

    // Read WF.log and get last line
    const data = fs.readFileSync(logFile, 'utf-8');

    // WF.log has different 'new line' character depending on OS sysyem
    if (process.platform == 'win32') {
        var lines = data.split(/\r\n/);
    } else if (process.platform == 'linux') {
        var lines = data.split(/\n/);
    }
    
    // console.log(lines);
    const workflowStatus = lines[lines.length-2];

    // Send last line
    e.reply('workflow-status-answer', workflowStatus);
})

// Local functions
function makeid(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

function runWorkflow (osType, modulesString, infile_user, workflowPath, infile_feature_info, e, workflow) {

    if (osType == 'linux') {
        script = path.join(__dirname, 'src', 'integrator.sh');
        batch = spawn('bash', [script, modulesString, infile_user, workflowPath, infile_feature_info, nCores]);
    } else if (osType == 'win32') {
        script = path.join(__dirname, 'src', 'integrator.bat');
        batch = spawn('CMD', ['/C', script, modulesString, infile_user, workflowPath, infile_feature_info, nCores]);
    }

    // console.log(script);
    // console.log("PID: ", batch.pid);

    batch.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    batch.stderr.on(`data`, (data) => {
        console.error(`stderr: ${data}`);
    });

    batch.on('close', (code) => {
        console.log(`child process exited with code ${code}`);

        // Handle
        if (code == 0) {
            // If exit code is 0, workflow was executed successfully
            var loadURL = win.loadURL(results);

            loadURL.then((val) => {
                // Remove WF.log file
                fs.unlinkSync(path.join(workflowPath, 'WF.log'));

                // When URL is loaded, send jobID
                e.reply('send-jobID', workflow);
            });

        } else if (!killed) {

            // Else, an error occurred
            var statusCode = code.toString();

            // If recognised error
            if (Object.keys(errorCode).includes(statusCode)) {
                var loadURL = win.loadURL(error);

                loadURL.then((val) => {
                    // When error page is loaded, send error information
                    e.reply('send-error', {"errorInfo": errorCode[statusCode], "workflow": workflow});
                });
            } else {
                // If error code is not recognised...
                var loadURL = win.loadURL(error);

                // Add to error object the unrecognised code error
                errorCode.NA.code = statusCode;

                loadURL.then((val) => {
                    // When error page is loaded, send information
                    e.reply('send-error', {"errorInfo": errorCode["NA"], "workflow": workflow})
                });
            }

        }
    });
}