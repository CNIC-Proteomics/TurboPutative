// Import modules
const fs = require('fs');
const path = require('path');

// Local function
importPartials = function (html) {

    // get folders
    let partialFolders = fs.readdirSync(path.join(__dirname, '../partials'), {withFileTypes:true}).reverse();

    partialFolders.forEach(folder => {

        if (folder.isDirectory()) {

            // get .html dirent from this partial folder
            let partialNames = fs.readdirSync(path.join(__dirname, '../partials', folder.name), {withFileTypes:true}).reverse();

            // check which partial should be added
            partialNames.forEach((file) => {
        
                if (file.isFile()) {
                    // if it is a file... 

                    let regex = new RegExp(`<!-- INSERT PARTIAL: ${folder.name}/${file.name} -->`, "g");

                    if (regex.test(html)) {
                        // if partial requirement is found, add it
                        let htmlPartial = fs.readFileSync(path.join(__dirname, `../partials/${folder.name}/${file.name}`));
                        html = html.replace(regex, htmlPartial);
                    }
                }


            });
            
        }

    })

    return html;
}

// Export function
module.exports = importPartials;