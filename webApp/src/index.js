const path = require('path');
const express = require('express');
const app = express();


// const { table } = require('console');

// settings
app.set('port', 8080);


// routes
app.use(require('./routes/routes.js'));


// set static files to be used
app.use(express.static(path.join(__dirname, "public")));


// 404 Not found
app.use((req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'notFound.html'));
})


// listening the server
app.listen(app.get('port'), function () {
    console.log('Server listening at port ', app.get('port'));
})
