// Global variables
var INIformat = 0; // 0 if format is correct; 1 otherwise
var lineError = 0; // Line with error format 

// Event added when user uploads regex file
document.getElementById('regexINI').addEventListener('change', function() { 
  
    var fr = new FileReader();

    // When file is uploaded, execute function to assert that format is correct
    fr.onload = function() { 
        assertINIFormat(fr.result);
    } 
    
    fr.readAsText(this.files[0]); 
})

// Function to assert ini format from string
function assertINIFormat(iniString) {
    
    // Split string in lines !!!BE CAREFUL WITH NATURAL \n!!!!1
    var lines = iniString.split(/[\r\n]+/g); // tolerate both Windows and Unix linebreaks

    // Define regular expressions used to assert the format
    var comment = /^#/;
    var nothing = /^\s*$/;
    var section = /^\[\w+\]\s*$/;
    var param = /^\w+\s=\s.*$/;

    var sectionCounter = 0; // 0 to open section; 1 for first param; 2 for second param

    for(i=0; i < lines.length; i++) {
        var line = lines[i];
        
        // If there is a comment or there is nothing, NEXT LINE
        if (comment.test(line) || nothing.test(line)) {
            continue;
        }

        // If openning a new section at the appropriate time, NEXT LINE
        if (section.test(line) && sectionCounter == 0) {
            sectionCounter += 1;
            continue;
        }

        // If first param definition, sum to sectionCounter and, NEXT LINE
        if (param.test(line) && sectionCounter == 1) {
            sectionCounter += 1;
            continue;
        }

        // If seconf param definition, reset sectionCounter and, NEXT LINE
        if (param.test(line) && sectionCounter == 2) {
            sectionCounter = 0;
            continue;
        }

        // If the iteration gets here, the format is not correct
        INIformat = 1;
        lineError = i+1;
        break;

    }

    if (INIformat == 0){
        console.log("Format is correct");
    } else {
        document.getElementById("errorINIFormat").style.display = "block";
        document.getElementById("errorINIFormat").innerHTML = `Format  error at line ${lineError}`;
        console.log(`Format error at line ${line}`);
    }
}