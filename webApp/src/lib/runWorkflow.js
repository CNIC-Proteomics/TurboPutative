// Import modules
const path = require("path");
const fs = require("fs");
const { exec } = require('child_process');

// Run workflow...
runWorkflow = function (fields, files, workflowID) {

    // promise is resolved when jobFolder is created
    return new Promise(resolve => {

        // create folder containing job
        console.log(`Creating folder for job ${workflowID}`);
        let jobFolder = path.join(__dirname, '../public/jobs/', workflowID);
        fs.mkdirSync(jobFolder);
        
        resolve(`jobFolder created: ${jobFolder}`); // promise is resolved, so server can ask for this folder

        // create object containing all parameters
        let parameters = JSON.parse(fields.iniInput);

        // create parameters .ini files
        for (let key in parameters.ini) {
            console.log(`Creating ${key}.ini file for job ${workflowID}`);
            fs.writeFileSync(path.join(jobFolder, `${key}.ini`), parameters.ini[key]);
        }

        // move files to jobFolder

            // infile
        console.log(`Copying infile to ${jobFolder}`);
        fs.copyFileSync(files.infile.path, path.join(jobFolder, files.infile.name));

            // featinfo file
        if (parameters.modules.includes("TableMerger")) {
            console.log(`Copying feature information filo to ${jobFolder}`)
            
            if (files.featInfoFile.size == 0) {
                console.log(`File with feature information has size 0 (it may not be uploaded)`);
                fs.writeFileSync(path.join(jobFolder, 'error.log'), '50');
                return;
            } else {
                fs.copyFileSync(files.featInfoFile.path, path.join(jobFolder, files.featInfoFile.name));
            }
        }

            // regex.ini file
        if (parameters.modules.includes("REname")) {
            console.log(`Copying regex.ini to ${jobFolder}`);

            if (files.regexFile.size == 0) {
                console.log(`Using default regex.ini`);
                fs.copyFileSync(path.join(__dirname, '../TurboPutative/config/configREname/regex.ini'), path.join(jobFolder, 'regex.ini'));
            } else {
                console.log(`Using regex.ini given by the user`);
                fs.copyFileSync(files.regexFile.path, path.join(jobFolder, 'regex.ini'));
            }

        }

        // run workflow
        let script = `bash "${path.join(__dirname, '../TurboPutative/integrator.sh')}"`;

        let workflowParam = "";
        for (let i=0; i<parameters.modules.length; i++) {
            switch (parameters.modules[i]) {
                case "Tagger":
                    workflowParam += '1';
                    break;
                
                case "REname":
                    workflowParam += '2';
                    break;
                
                case "RowMerger":
                    workflowParam += '3';
                    break;
                
                case "TableMerger":
                    workflowParam += '4';
                    break;
            }
            
        }

        let infileParam = path.join(jobFolder, files.infile.name);
        let featInfoFileParam = parameters.modules.includes("TableMerger") ? path.join(jobFolder, files.featInfoFile.name) : "";

        let fullCommand = `${script} ${workflowParam} "${infileParam}" "${jobFolder}" "${featInfoFileParam}"`;
        console.log(`Executing workflow: ${fullCommand}`);
        exec(fullCommand, (error, stdout, stderr) => {
            if (error) {
                console.error(`exec error: ${error}`);
                fs.writeFileSync(path.join(jobFolder, 'error.log'), error.code);
                return;
            }
            fs.writeFileSync(path.join(jobFolder, 'log.info'), `stdout:\n${stdout}\nstderr:\n${stderr}`);
            console.log(`stdout: ${stdout}`);
            console.error(`stderr: ${stderr}`);
            console.log(`Finished workflow execution: ${workflowID}`);
        });


    })

}

// Export module
module.exports = runWorkflow;