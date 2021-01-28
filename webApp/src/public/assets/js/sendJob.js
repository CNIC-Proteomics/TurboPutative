// Add event to RUN button
//let lastElem = document.querySelector(`#${workflowObject.modules[workflowObject.modules.length-1]}ParamContent .run`);

sendJob = function () {
    
    // ASSERTS
    let errorElem = document.querySelector(`#${workflowObject.modules[workflowObject.modules.length-1]}ParamContent .errorRun`);
    errorElem.style.display = 'none';

    // Assert that at least one tag was selected
    let tagsElemNodeList = document.querySelectorAll("#TaggerParamContent input[type='checkbox']")
    let tagCheckedArray = [];

    for (let i=0; i<tagsElemNodeList.length; i++) {
        tagCheckedArray.push(!tagsElemNodeList[i].checked);
    }

    if (tagCheckedArray.every((item)=>item) && workflowObject.modules.includes("Tagger")) {
        errorElem.innerHTML = "Select one tag in Tagger module";
        errorElem.style.display = 'block';
        return;
    }

    // Assert that at least one column was given in RowMerger
    /*
    if ((document.querySelector("#comparedCol").value == "" || document.querySelector("#conservedCol").value == "") && workflowObject.modules.includes("RowMerger")) {
        errorElem.innerHTML = "Write at least one column in 'Conserved Columns' and 'Comapred Columns' RowMerger parameters";
        errorElem.style.display = 'block';
        return;
    }
    */

    // Assert that table with feature information was given
    if (workflowObject.modules.includes("TableMerger") && !workflowObject.featInfoFile) {
        errorElem.innerHTML = "Introduce file with feature information (TableMerger)";
        errorElem.style.display = 'block';
        return;
    }

    // CREATE INI
    workflowObject.modules.forEach((elem) => {
        workflowObject[`iniMaker${elem}`]();
    }) 

    // CREATE STRING JSON WITH MODULES AND INI
    iniInput.value = JSON.stringify({"modules": workflowObject.modules, "ini": workflowObject.ini});

    console.log(iniInput);

    // SUBMIT
    workflowForm.submit();
}