// Import modules
const express = require("express");
const formidable = require("formidable");
const fs = require('fs');
const path = require('path');
const importPartials = require(path.join(__dirname, '../lib/importPartials.js'));
const importValues = require(path.join(__dirname, '../lib/importValues.js'));
const runWorkflow = require(path.join(__dirname, '../lib/runWorkflow.js'));
const makeid = require(path.join(__dirname, '../lib/makeid.js'));
const execTime = require(path.join(__dirname, '../lib/execTime.js'));

// Global variables
var views = path.join(__dirname, '../views');
var router = express.Router();

// Workflow is sent from client...
router.post('/execute', (req, res) => {

    // create workflow ID
    let workflowID = makeid(5);

    // handle post request
    const form = formidable({ multiples: true });
    
    form.parse(req, async (err, fields, files) => {

        if (err) {
            next(err);
            return;
        }

        // run workflow
        msg = await runWorkflow(fields, files, workflowID);
        console.log(msg);

        // redirect to /execute/:id...
        res.redirect(`execute/${workflowID}`);
    })

})


// It is asked for a job from client...
router.get('/execute/:id', (req, res) => { 
    
    let jobFolder = path.join(__dirname, '../public/jobs/', req.params.id);

    // Check workflow status...
    if (!fs.existsSync(jobFolder)) {
        // Assert that folder exists

        console.log(`The following folder does not exist: ${req.params.id}`);
        console.log("Send not found page");

        // not found job error
        let codeError = 51;
        let codeErrorJSON = JSON.parse(fs.readFileSync(path.join(__dirname, '../TurboPutative/errorCode.json'), 'utf-8'));

        // read html view and import partials
        let html = importPartials(fs.readFileSync(path.join(views, "error.html"), "utf-8"));

        // import values
        html = importValues(html, {
            "<!-- INSERT VALUE: code -->": `${codeError}`,
            "<!-- INSERT VALUE: errorLocation -->": `${codeErrorJSON[codeError]["module"]}`,
            "<!-- INSERT VALUE: errorDescription -->": `${codeErrorJSON[codeError]["description"]}`
        })

        // send complete html
        res.send(html);
    
    } else if (fs.existsSync(path.join(jobFolder, 'TurboPutativeResults.zip'))) {
        // The folder does exist && TurboPutativeResults.zip exist --> Send results

        console.log(`The following job finished: ${req.params.id}`);
        console.log("Send downloading page");

        // read html view and import partials
        let html = fs.readFileSync(path.join(views, "loading.html"), "utf-8");

        // import values
        html = importValues(html, {
            "/* INSERT VALUE: workflowID */": `${req.params.id}`,
            "/* INSERT VALUE: status */": "Finished",
            "<!-- INSERT VALUE: partialButton -->": "<!-- INSERT PARTIAL: execute/downloadButton.html -->",
            "/* INSERT VALUE: execTime */": execTime(fs.statSync(path.join(__dirname, '../public/jobs', req.params.id)).birthtimeMs,
                fs.statSync(path.join(__dirname, '../public/jobs', req.params.id, 'TurboPutativeResults.zip')).birthtimeMs)
        });

        html = importPartials(html);

        html = importValues(html, {
            "/* INSERT VALUE: linkToZip */": `${path.join('/jobs/', req.params.id, 'TurboPutativeResults.zip')}`
        })

        // send complete html
        res.send(html);

    } else if (fs.existsSync(path.join(__dirname, '../public/jobs', req.params.id, 'error.log'))) {
        // The folder exists && TurboPutative.zip does not exist --> check if error.log file exists (workflow failed...)

        console.log(`The following job failed: ${req.params.id}`);
        console.log("Send error page");

        // get code error
        let codeError = fs.readFileSync(path.join(__dirname, '../public/jobs', req.params.id, 'error.log'), 'utf-8');
        let codeErrorJSON = JSON.parse(fs.readFileSync(path.join(__dirname, '../TurboPutative/errorCode.json'), 'utf-8'));

        // if codeError is in codeErrorJSON, we use it later for extraction. Otherwise, use NA
        let codeErrorAdapt = Object.keys(codeErrorJSON).includes(codeError) ? codeError : "NA";

        // read html view and import partials
        let html = importPartials(fs.readFileSync(path.join(views, "error.html"), "utf-8"));

        // import values
        html = importValues(html, {
            "<!-- INSERT VALUE: code -->": `${codeError}`,
            "<!-- INSERT VALUE: errorLocation -->": `${codeErrorJSON[codeErrorAdapt]["module"]}`,
            "<!-- INSERT VALUE: errorDescription -->": `${codeErrorJSON[codeErrorAdapt]["description"]}`
        })

        // send complete html
        res.send(html);

    } else {
        // Folder exists && TurboPutative.zip is not created && error.log is not created --> wait...
        
        console.log(`The following job did not finished: ${req.params.id}`);
        console.log("Send loading page");

        // read html view and import partials
        let html = importPartials(fs.readFileSync(path.join(views, "loading.html"), "utf-8"));

        // import values
        html = importValues(html, {
            "/* INSERT VALUE: workflowID */": `${req.params.id}`,
            "/* INSERT VALUE: status */": "Running",
            "<!-- INSERT VALUE: reload.js -->": `<script type='text/javascript' src='${path.join('/assets/js/reload.js')}'></script>`,
            "/* INSERT VALUE: execTime */": execTime(fs.statSync(path.join(__dirname, '../public/jobs', req.params.id)).birthtimeMs, new Date().getTime())
        });

        // send complete html
        res.send(html);

    }

})

// Export Route
module.exports = router;