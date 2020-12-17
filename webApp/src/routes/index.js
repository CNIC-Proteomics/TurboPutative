// Import modules
const express = require("express");
const fs = require('fs');
const path = require('path');
const importPartials = require(path.join(__dirname, '../lib/importPartials.js'));

// Global variables
var router = express.Router();
var views = path.join(__dirname, '../views');

// Set routes
router.get('/', (req, res) => {
    // send main page
    console.log("Send main page");

    // read html view and import partials
    let html = importPartials(fs.readFileSync(path.join(views, "main.html"), "utf-8"));

    // send complete html
    res.send(html);
})

router.get('/execute', (req, res) => {
    // send execute page
    console.log("Send execute page");

    // read html view and import partials
    let html = importPartials(fs.readFileSync(path.join(views, "execute.html"), "utf-8"));

    // send complete html
    res.send(html);
})

router.get('/contactUs', (req, res) => {
    // send contact us page
    console.log("Send contact us page");

    // read html view and import partials
    let html = importPartials(fs.readFileSync(path.join(views, "contactUs.html"), "utf-8"));

    // send complete html
    res.send(html);
})

router.get('/modules', (req, res) => {
    // send modules page
    console.log("Send modules page");

    // read html view and import partials
    let html = importPartials(fs.readFileSync(path.join(views, "modules.html"), "utf-8"));
    
    // send complete html
    res.send(html);
})

router.get('/settings', (req, res) => {
    // send modules page
    console.log("Send settings page");

    // read html view and import partials
    let html = importPartials(fs.readFileSync(path.join(views, "settings.html"), "utf-8"));
    
    // send complete html
    res.send(html);
})


// Export Route
module.exports = router;