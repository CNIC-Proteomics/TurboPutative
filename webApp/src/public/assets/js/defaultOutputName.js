// When user uploads a file, get its name
document.querySelector("#infile").addEventListener("change", () => {
    defaultValues.Ubiquitous.filename = document.querySelector('#infile').files[0].name;

    // set output default name in tooltips
    document.querySelector('#TaggerONTTT').innerHTML += `${workflowObject.modules.indexOf("Tagger")+1}_Tagged_${defaultValues.Ubiquitous.filename}`;
    document.querySelector('#REnameONTTT').innerHTML += `${workflowObject.modules.indexOf("REname")+1}_REnamed_${defaultValues.Ubiquitous.filename}`;
    document.querySelector('#RowMergerONTTT').innerHTML += `${workflowObject.modules.indexOf("RowMerger")+1}_RowMerged_${defaultValues.Ubiquitous.filename}`;
    document.querySelector('#TableMergerONTTT').innerHTML += `${workflowObject.modules.indexOf("TableMerger")+1}_TableMerged_${defaultValues.Ubiquitous.filename}`;
});