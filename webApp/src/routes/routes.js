const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');
const formidable = require('formidable');
const workflowExecution = require(path.join(__dirname, 'workflowExecution.js'));


// global variables
const src = path.join(__dirname, '..');
const public = path.join(src, 'public');
const partial = path.join(src, 'partial');
const errorCode = JSON.parse(fs.readFileSync(path.join(public, 'assets', 'files', 'errorCode.json'), 'utf-8'));

// ROUTES

router.get('/', (req, res) => {
    res.sendFile(path.join(public, "index.html"));
})

// TurboPutative workflow handling
router.post('/turboputative.html', function(req, res) {

    const form = formidable({ multiples: true });

    form.parse(req, function (err, fields, files) {
        
        if (err) throw err;

        // run workflow
        allModulesParams = workflowExecution.paramObjectsCreator(fields);
        workflow = fields["workflow"].split("");
        jobID = fields["jobID"];
        workflowExecution.executeWorkFlow(allModulesParams, workflow, jobID, files);

        // send "waiting" page to the client
        fs.readFile(path.join(partial, "putativejob.html"), "utf-8", function (err, html) {
            if (err) throw err;

            html = html.replace("###INSERT_JOB_ID###", jobID);
            html = html.replace("###INSERT_JOB_STATUS###", 'Processing');
            html = html.replace("###INSERT_DURATION###", 0);

            //res.writeHead(200, {'Content-type':'text/plain'});
            res.send(html);
            res.end();
        })

        // console.log(allModulesParams);
        // console.log(JSON.stringify({ fields, files }, null, 2));
    })

})

// Reloading handling
router.get('/turboputative.html/:id', function (req, res) { 

    var jobID = req.params.id;

    // Assert that jobID folders exists, and get its birth date
    fs.stat(path.join(public, 'results', jobID), (err, stats) => {

        // If folder does not exists, send notFound
        if(err) {

            res.sendFile(path.join(public, "jobNotFound.html"));
        
        // Else, look how is the workflow execution
        } else {

            // If log_error.json exists, workflow execution failed. Otherwise, it is running or it finished.
            fs.readFile(path.join(public, 'results', jobID, 'log_error.json'), 'utf-8', (err, logError) => {

                // If log_error.json does not exist, it goes well (until now at least)
                if (err) {

                    // Get folder birth date
                    var date1 = stats.birthtime;

                    // If .zip file exist, workflow finished. Otherwise, it is still running
                    fs.stat(path.join(public, 'results', jobID, 'TurboPutativeResults.zip'), function(err, stats){
                    
                        // If .zip does not exist...
                        if (err){

                            // send "waiting" page to the client (after parsing)
                            fs.readFile(path.join(partial, "putativejob.html"), "utf-8", function (err, html) {
                                if (err) throw err;

                                // Get process time
                                var date2 = new Date();
                                var duration =  date2 - date1;

                                html = html.replace("###INSERT_JOB_ID###", jobID);
                                html = html.replace("###INSERT_JOB_STATUS###", 'Processing');
                                html = html.replace("###INSERT_DURATION###", duration);

                                //res.writeHead(200, {'Content-type':'text/plain'});
                                res.send(html);
                                res.end();
                            })

                        // If .zip file exists...
                        } else {

                            // Calculate difference between folder and .zip creation
                            var date2 = stats.birthtime;
                            var duration = date2 - date1;

                            // Send final page (after parsing it)
                            fs.readFile(path.join(partial, "putativejob.html"), "utf-8", function (err, html) {
                                if (err) throw err;

                                html = html.replace("###INSERT_JOB_ID###", jobID);
                                html = html.replace("###INSERT_JOB_STATUS###", 'Finished');
                                html = html.replace("###INSERT_DURATION###", duration);
                                html = html.replace("###INSERT_ZIP_PATH###", path.join('..', 'results', jobID, 'TurboPutativeResults.zip'));

                                containerDownloadDisplay = "document.getElementById('containerDownload').style.display = 'block'"
                                html = html.replace("//###INSERT_DISPLAY_containerDownload###", containerDownloadDisplay);

                                html = html.replace(/setTimeout.*\n/g, "");

                                res.send(html);
                                res.end();
                            })
                        }
                    })
                
                // If log_error.json exists, send executionError.html (after parsing it)
                } else {
                    
                    fs.readFile(path.join(partial, 'executionError.html'), 'utf-8', (err, html) => {
                        if (err) throw err;
                        
                        logError = logError.replace('\n', ''); // Remove final \n
                        console.log(logError);
                        console.log(errorCode[logError]);

                        if (Object.keys(errorCode).includes(logError)) {
                            // If the error is recognised...

                            var errorInfo = JSON.stringify(errorCode[logError]);
                            console.log(errorInfo);
                            // logError = logError.replace('\n', ''); // Remove final \n
                            html = html.replace("'###INSERT_LOG_ERROR###'", errorInfo);
                            res.send(html);  

                        } else {
                            // If the error is not recognised...
                            var errorInfo = JSON.stringify(errorCode['NA']);
                            html = html.replace("'###INSERT_LOG_ERROR###'", errorInfo);
                            res.send(html); 
                        }



                    })
                }
            })
        }
    })
})

module.exports = router;