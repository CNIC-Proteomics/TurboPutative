// Import modules
const path = require("path");
const fs = require("fs");

// Generate specific id
function makeid(length) {
    var result           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;

    do {
        // Until result is not contained in jobs folder...
        for ( var i = 0; i < length; i++ ) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
         }

    } while (fs.readdirSync(path.join(__dirname, '../public/jobs')).includes(result)) ;
    
    return result;
 }

 // Export function
 module.exports = makeid;