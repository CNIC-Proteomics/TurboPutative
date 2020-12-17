// When pressing "Select all", check all...
let allTagsElem = document.querySelector("#allTags")

selectTags = function () {

    if (allTagsElem.checked) {

        document.querySelector("#food").checked = true;
        document.querySelector("#drug").checked = true;
        document.querySelector("#peptide").checked = true;
        document.querySelector("#halogenated").checked = true;

    } else {

        document.querySelector("#food").checked = false;
        document.querySelector("#drug").checked = false;
        document.querySelector("#peptide").checked = false;
        document.querySelector("#halogenated").checked = false;

    }
}

allTagsElem.addEventListener("change", selectTags, false);


// If select all is selected, one tag is deselected, deselect all
deselectAll = function () {
    if (!this.checked && allTagsElem.checked) {
        allTagsElem.checked = false;
    } 
}

document.querySelector("#food").addEventListener("change", deselectAll, false);
document.querySelector("#drug").addEventListener("change", deselectAll, false);
document.querySelector("#peptide").addEventListener("change", deselectAll, false);
document.querySelector("#halogenated").addEventListener("change", deselectAll, false);