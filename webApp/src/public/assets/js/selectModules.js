/* Add click event to .moduleButton */

// Get node list with every button
var moduleButtonNodeList = document.querySelectorAll(".moduleButton");

// Function to show selected module after onclick
showSelectedModule = function () {
    
    // If module has been selected, exit
    if (workflowObject.modules.includes(this.innerHTML)) {
        return;
    };

    // Add selected module to workflowObect.modules
    workflowObject.modules.push(this.innerHTML);

    // Show element
    let element = workflowObject.modules.length == 1 ? `<span class='selectedModule'>${this.innerHTML}</span>` : 
                                                        `<span class='rarr'>&rarr;</span><span class='selectedModule'>${this.innerHTML}</span>`;
    
    document.querySelector("#moduleSelectionContent").innerHTML += `${element}`;

    // Change color of the button
    this.style.backgroundColor = "darkred";
    this.style.color = "white";

    // Show block with selected modules
    if (workflowObject.modules.length == 1) {
        document.querySelector("#selectedContent").style.display = "block";
    };
};

// Add event to each button element
for (let i=0; i< moduleButtonNodeList.length; i++) {
    moduleButtonNodeList[i].addEventListener("click", showSelectedModule, false);
};