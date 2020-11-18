const fs = require('fs');
const {spawn} = require('child_process');
const path = require('path');

// global variables
public = path.join(__dirname, '..', 'public');

// Functions used to execute the workflow

paramObjectsCreator = function(paramJSON) {

    var taggerParams = paramJSON.TaggerParams;
    var modParams = paramJSON.ModParams;
    var tableParams = paramJSON.TableParams;
    var featureInfoParams = paramJSON.FeatureInfoParams;
    
    var allModulesParams = {Tagger: taggerParams, REname: modParams, RowMerger: tableParams, TableMerger: featureInfoParams};
  
    return allModulesParams;
}


executeWorkFlow = function(allModulesParams, workflow, jobID, files) {

    jobDir = path.join(public, 'results', jobID);

    fs.access(jobDir, function (err) {

        if (err){
            fs.mkdir(jobDir, function(err) {
                if (err) throw err;
                
                infile_user = path.join(jobDir, files['inputFile']['name']);

                fs.copyFile(files['inputFile']['path'], infile_user, function (err){
                    if (err) throw err;

                    console.log(jobDir + " directory successfully created");
                    executeModules(allModulesParams, workflow, jobID, infile_user, files);            
                })

            })
        }
    })
}


executeModules = function(allModulesParams, workflow, jobID, infile_user, files) {

    numToMod = {1: 'Tagger', 2: 'REname', 3: 'RowMerger', 4: 'TableMerger'}
    infile_feature_info = "";
    workflow_string = workflow.toString().replace(/,/g, "");
    jobDir = path.dirname(infile_user);

    for (moduleNum of workflow) {
        moduleName = numToMod[moduleNum];

        switch (moduleName) {
            
            case "Tagger":
                iniWriter(allModulesParams[moduleName], jobDir, "Tagger.ini");
                break;
            
            case "REname":
                iniWriter(allModulesParams[moduleName], jobDir, "REname.ini");
                
                // If user does not upload regex.ini file, copy it from config
                if (files["regexINI"]["size"] == 0){
                    fs.copyFile(path.join(public, "..", "tools", "config", "configREname", "regex.ini"), path.join(jobDir, "regex.ini"), (err) => {
                        if (err) throw err;
                    })
                } else {
                    fs.copyFile(files["regexINI"]["path"], path.join(jobDir, "regex.ini"), (err) => {
                        if (err) throw err;
                    })
                }
                break;

            case "RowMerger":
                iniWriter(allModulesParams[moduleName], jobDir, "RowMerger.ini");
                break;
            
            case "TableMerger":
                outfile = iniWriter(allModulesParams[moduleName], jobDir, "TableMerger.ini");
                infile_feature_info = path.join(jobDir, files["FeatureInfo_file"]["name"]);
                fs.copyFile(files["FeatureInfo_file"]["path"], infile_feature_info, function (err) {
                    if (err) throw err;
                })
                break;
        }
    }

    script = path.join(__dirname, '..', 'tools', 'integrator.sh');
    console.log(script);

    const bash = spawn('bash', [script, workflow_string, infile_user, jobDir, jobID, infile_feature_info]);

    bash.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    bash.stderr.on(`data`, (data) => {
        console.error(`stderr: ${data}`);
    });

    bash.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });


}

iniWriter = function (iniString, jobDir, module) {
    
    iniWrite = iniString.replace(/###/g, '\n');

    filePath = path.join(jobDir, module);
    fs.writeFile(filePath, iniWrite, function (err) {
        if (err) throw err;

        console.log(module + " was saved");
    })
}

// Export module
module.exports.paramObjectsCreator = paramObjectsCreator;
module.exports.executeWorkFlow = executeWorkFlow;