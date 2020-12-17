// Assign click event to next buttons
let nextElementNodeList = document.querySelectorAll(".next");

nextAction = function () {

    if (viewExecute == -2) {
        document.querySelector("#selectorContent").style.display = "none";
        document.querySelector("#infileContent").style.display = "block";
        //document.querySelector(`#TableMergerParamContent`).style.display = "block";

        lastElemRun = document.querySelector(`#${workflowObject.modules[workflowObject.modules.length-1]}ParamContent .run`);
        document.querySelector(`#${workflowObject.modules[workflowObject.modules.length-1]}ParamContent .next`).style.display = "none";
        lastElemRun.style.display = "block";

        lastElemRun.addEventListener("click", sendJob, false);
    }

    if (viewExecute == -1) {
        document.querySelector("#infileContent").style.display = "none";
        document.querySelector(`#${workflowObject.modules[0]}ParamContent`).style.display = "block";
    }

    if (viewExecute > -1) {
        document.querySelector(`#${workflowObject.modules[viewExecute]}ParamContent`).style.display = "none";
        document.querySelector(`#${workflowObject.modules[viewExecute+1]}ParamContent`).style.display = "block";
    }

    viewExecute += 1;

}

for (let i=0; i<nextElementNodeList.length; i++) {
    nextElementNodeList[i].addEventListener("click", nextAction, false);
}


// Assign click event to previous buttons
let previousElementNodeList = document.querySelectorAll(".previous");

previousAction = function () {

    if (viewExecute == -2) {
        location.reload();
    }

    if (viewExecute == -1) {
        document.querySelector("#infileContent").style.display = "none";
        document.querySelector("#selectorContent").style.display = "block";
    }

    if (viewExecute == 0) {
        document.querySelector(`#${workflowObject.modules[0]}ParamContent`).style.display = "none";
        document.querySelector("#infileContent").style.display = "block";
    }

    if (viewExecute > 0) {
        document.querySelector(`#${workflowObject.modules[viewExecute]}ParamContent`).style.display = "none";
        document.querySelector(`#${workflowObject.modules[viewExecute-1]}ParamContent`).style.display = "block";
    }

    viewExecute -= 1

}

for (let i=0; i<previousElementNodeList.length; i++) {
    previousElementNodeList[i].addEventListener("click", previousAction, false);
}


// Show next button when infile is uploaded
showNextInfile = function () {
    document.querySelector("#infileContent .next").style.display = "block";
}

document.querySelector("#infile").addEventListener("change", showNextInfile, false);

// Click advance button
clickAdvance = function (elemQuery) {
    document.querySelector(elemQuery).style.display = document.querySelector(elemQuery).style.display == "none" ? "block" : "none";
}