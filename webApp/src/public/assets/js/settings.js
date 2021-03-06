// Global variables
var workflowObject = {
    
    "modules": [],

    "featInfoFile": false,

    "ini": {},

    "iniMakerTagger": function () {
        this.ini.Tagger = "";

        this.ini.Tagger += "[TagSelection]";
        this.ini.Tagger += "####";
        this.ini.Tagger += "Food = ";
        this.ini.Tagger += document.querySelector("#food").checked;
        this.ini.Tagger += "####";
        this.ini.Tagger += "Drug = ";
        this.ini.Tagger += document.querySelector("#drug").checked;
        this.ini.Tagger += "####"
        this.ini.Tagger += "MicrobialCompound = ";
        this.ini.Tagger += document.querySelector("#microbial").checked;
        this.ini.Tagger += "####"
        this.ini.Tagger += "Plant = ";
        this.ini.Tagger += document.querySelector("#plant").checked;
        this.ini.Tagger += "####"
        this.ini.Tagger += "NaturalProduct = ";
        this.ini.Tagger += document.querySelector("#naturalProduct").checked;
        this.ini.Tagger += "####"
        this.ini.Tagger += "Halogenated = ";
        this.ini.Tagger += document.querySelector("#halogenated").checked;
        this.ini.Tagger += "####"
        this.ini.Tagger += "Peptide = ";
        this.ini.Tagger += document.querySelector("#peptide").checked;
        this.ini.Tagger += "####"

        this.ini.Tagger += "[Parameters]";
        this.ini.Tagger += "####";
        this.ini.Tagger += "HalogenatedRegex = ";
        this.ini.Tagger += document.querySelector("#halogenatedRegex").value == "" ? defaultValues.Tagger.halogenatedRegex : document.querySelector("#halogenatedRegex").value;
        this.ini.Tagger += "####";
        this.ini.Tagger += "PeptideRegex = ";
        this.ini.Tagger += document.querySelector("#peptideRegex").value == "" ? defaultValues.Tagger.peptideRegex : document.querySelector("#peptideRegex").value;
        this.ini.Tagger += "####";
        this.ini.Tagger += "OutputColumns = "
        this.ini.Tagger += document.querySelector("#outputColumnsTagger").value;
        this.ini.Tagger += "####";
        this.ini.Tagger += "OutputName = ";
        this.ini.Tagger += document.querySelector("#outputNameTagger").value != "" ? document.querySelector("#outputNameTagger").value : 
            `${this.modules.indexOf("Tagger")+1}_Tagged_${document.querySelector("#infile").files[0].name}`;
        
        this.ini.Tagger = this.ini.Tagger.replace(/####/g, "\n");
    },

    "iniMakerREname": function () {
        this.ini.REname = "";

        this.ini.REname += "[Parameters]";
        this.ini.REname += "####";
        this.ini.REname += "RemoveRow = ";
        this.ini.REname += document.querySelector("#removeRowRegex").value == "" ? defaultValues.REname.removeRowRegex: document.querySelector("#removeRowRegex").value;
        this.ini.REname += "####";
        this.ini.REname += "Separator = ";
        this.ini.REname += document.querySelector("#separator").value == "" ? defaultValues.REname.compoundSeparator : document.querySelector("#separator").value;
        this.ini.REname += "####";
        this.ini.REname += "AminoAcidSeparator = ";
        this.ini.REname += document.querySelector("#aaSeparator").value == "" ? defaultValues.REname.aminoAcidSeparator : document.querySelector("#aaSeparator").value;
        this.ini.REname += "####";
        this.ini.REname += "OutputColumns = ";
        this.ini.REname += document.querySelector("#outputColumnsREname").value;
        this.ini.REname += "####";
        this.ini.REname += "OutputName = "
        this.ini.REname += document.querySelector("#outputNameREname").value != "" ? document.querySelector("#outputNameREname").value : 
            `${this.modules.indexOf("REname")+1}_REnamed_${document.querySelector("#infile").files[0].name}`;

        this.ini.REname = this.ini.REname.replace(/####/g, "\n");
    },

    "iniMakerRowMerger": function () {
        this.ini.RowMerger = "";

        this.ini.RowMerger += "[Parameters]";
        this.ini.RowMerger += "####";
        this.ini.RowMerger += "ComparedColumns = ";
        this.ini.RowMerger += document.querySelector("#comparedCol").value == "" ? defaultValues.RowMerger.comparedColumns : document.querySelector("#comparedCol").value;
        this.ini.RowMerger += "####";
        this.ini.RowMerger += "ConservedColumns = ";
        this.ini.RowMerger += document.querySelector("#conservedCol").value == "" ? defaultValues.RowMerger.conservedColumns : document.querySelector("#conservedCol").value;
        this.ini.RowMerger += "####";
        this.ini.RowMerger += "OutputColumns = ";
        this.ini.RowMerger += document.querySelector("#outputColumnsRowMerger").value;
        this.ini.RowMerger += "####";
        this.ini.RowMerger += "OutputName = "
        this.ini.RowMerger += document.querySelector("#outputNameRowMerger").value != "" ? document.querySelector("#outputNameRowMerger").value : 
            `${this.modules.indexOf("RowMerger")+1}_RowMerged_${document.querySelector("#infile").files[0].name}`;
        
        this.ini.RowMerger = this.ini.RowMerger.replace(/####/g, "\n");
    },

    "iniMakerTableMerger": function () {
        this.ini.TableMerger = "";

        this.ini.TableMerger += "[Parameters]";
        this.ini.TableMerger += "####";
        this.ini.TableMerger += "N_Digits = ";
        this.ini.TableMerger += document.querySelector("#decimalPlaces").value == "" ? defaultValues.TableMerger.decimalPlaces : document.querySelector("#decimalPlaces").value;
        this.ini.TableMerger += "####";
        this.ini.TableMerger += "OutputColumns = ";
        this.ini.TableMerger += document.querySelector("#outputColumnsTableMerger").value;
        this.ini.TableMerger += "####";
        this.ini.TableMerger += "OutputName = "
        this.ini.TableMerger += document.querySelector("#outputNameTableMerger").value != "" ? document.querySelector("#outputNameTableMerger").value : 
            `${this.modules.indexOf("TableMerger")+1}_TableMerged_${document.querySelector("#infile").files[0].name}`;
        
        this.ini.TableMerger = this.ini.TableMerger.replace(/####/g, "\n");
    },

};

var viewExecute = -2;   // Variable to indicate which view is being showed in execute.html
                        // -2: Select modules
                        // -1: Input file
                        // 0-3: Selected modules

// Create form used to send job to server
var workflowForm = document.createElement("form");
workflowForm.setAttribute('style', 'display:none;')
workflowForm.setAttribute('id', 'workflowForm');
workflowForm.setAttribute('method', 'post');
workflowForm.setAttribute('action', '/execute');
workflowForm.setAttribute('enctype', "multipart/form-data");
document.querySelector('body').appendChild(workflowForm);

var iniInput = document.createElement("input");
iniInput.setAttribute("form", "workflowForm");
iniInput.setAttribute("id", "iniInput");
iniInput.setAttribute("name", "iniInput");
iniInput.setAttribute("type", "text");
workflowForm.appendChild(iniInput);