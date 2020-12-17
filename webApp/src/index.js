// Import modules
const express = require('express');
const morgan = require('morgan');
const path = require('path');

// Global variables
var app = express();

// Settings
app.set('port', 8080);

// Middlewares
app.use(morgan('combined'));

// Routes
app.use(require(path.join(__dirname, "routes/index.js")));
app.use(require(path.join(__dirname, "routes/execute.js")));

// Static files
app.use(express.static(path.join(__dirname, 'public')));

// Start listening
app.listen(app.get('port'), () => {
    console.log('TurboPutative web application listening on port', app.get('port'));
})