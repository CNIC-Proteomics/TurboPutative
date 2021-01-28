// Global variables
var buttonNodeList = document.querySelectorAll("#moduleContent div");
var textNodeList = document.querySelectorAll(".text");

// Show Tagger module by default
textNodeList[0].style.display = "block";
buttonNodeList[0].style.backgroundColor = "rgba(139,0,0,0.9)";
buttonNodeList[0].style.color = "rgba(255,255,255,0.9)";

// document.querySelector("#TaggerText").style.display = "block";
// document.querySelector("#TaggerButton").style.backgroundColor = "rgba(139,0,0,0.9)";
// document.querySelector("#TaggerButton").style.color = "rgba(255,255,255,0.9)";

// Add event to each button
clickButton = function () {

    // display:none to every text
    textNodeList.forEach(elem => {
        elem.style.display = "none"
    })

    // display:"block" to text selected by user
    document.querySelector(`#${this.innerHTML}Text`).style.display = "block";

    // background-color: "default" to evey button
    buttonNodeList.forEach(elem => {
        elem.style.backgroundColor = "rgba(139,0,0,0.6)";
    })

    // background-color & color: "hover" to button selected by user
    this.style.backgroundColor = "rgba(139,0,0,0.9)";
    this.style.color = "rgba(255,255,255,0.9)";

}

buttonNodeList.forEach(elem => {
    elem.addEventListener("click", clickButton);
});