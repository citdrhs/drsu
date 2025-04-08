//Links logo to home page
const logo = document.getElementById('homePage');
logo.addEventListener('click', function() {
    //Updated for routing when connected with backend
    window.location.href = "/homePage"
})

//ABOVE CODE WORKS WITH BACKEND: DO NOT COPY AND PASTE ABOVE THIS POINT

document.addEventListener("DOMContentLoaded",function(){
    addTable("appetizer",10);
    addTable("desserts",5);
})

////////////////////////////////////////////////////////////////////////////
//Functions
////////////////////////////////////////////////////////////////////////////

function addItem() {
    profanitylist = ["bitch", "fuck", "ass", "nigga", "retarded", "cunt","shit","nigger","chink","gay","sex","jerk off","cum", "masterbate","motherfucker","whore","penis","pussy","retard","blowjob","slut","cock"]
    //Creates a new row with name, dish, and email info
    if(
        document.getElementById("nameInput").value == "" ||
        document.getElementById("dishNameInput").value == "" ||
        document.getElementById("emailInput").value == ""
        ){
        document.getElementById("confirm").innerHTML = "Please fill in indicated fields";
        document.getElementById("confirm").style.color = "red";
        document.getElementById("confirm").style.fontWeight = "bold";
        if(document.getElementById("nameInput").value == ""){
            document.getElementById("nameInput").style.border = "3px solid red";
        } else {
            document.getElementById("nameInput").style.border = "1px solid black";
        }
        if(document.getElementById("dishNameInput").value == ""){
            document.getElementById("dishNameInput").style.border = "3px solid red";
        } else {
            document.getElementById("dishNameInput").style.border = "1px solid black";
        }
        if(document.getElementById("emailInput").value == ""){
            document.getElementById("emailInput").style.border = "3px solid red";
        } else {
            document.getElementById("emailInput").style.border = "1px solid black";
        }
    }  else if(
        profanitylist.includes(document.getElementById("nameInput").value.trim().toLowerCase()) || 
        profanitylist.includes(document.getElementById("dishNameInput").value.trim().toLowerCase())
    ){
        alert("profanity detected, instance sent to event lead");
        document.getElementById("nameInput").value = "";
        document.getElementById("dishNameInput").value = "";
    }
    else {
        document.querySelector("#" + tableid + "Signup tfoot").innerHTML = "";

        const newtr = document.createElement("tr");
        const name = document.createElement("td");
        name.innerHTML = document.getElementById("nameInput").value;
        const item = document.createElement("td");
        item.innerHTML = document.getElementById("dishNameInput").value;
        const email = document.createElement("td");
        email.innerHTML = document.getElementById("emailInput").value;

        const close = document.createElement("td");
        const close_button = document.createElement("img"); 
        /*close_button.innerHTML = "close"*/
        close_button.src = "CloseButton.png";
        close_button.style.cursor = "pointer";
        
        close.appendChild(close_button);

        newtr.appendChild(name);
        newtr.appendChild(item);
        newtr.appendChild(email);
        newtr.appendChild(close)
        
        //Adds new row to tbody
        document.querySelector("#" + tableid + "Signup tbody").appendChild(newtr);
        console.log(newtr.parentElement.parentElement.id);
        //Updates count of signed up people

        //hiding input section and clearing inputs

        document.getElementById("inputs").style.setProperty("display", "none", "important");
        document.getElementById("nameInput").value = "";
        document.getElementById("dishNameInput").value = "";
        document.getElementById("emailInput").value = "";
        
        //Any check boxes added will need to have class of checkbox
        let checkboxes = document.querySelectorAll("#inputs .checkbox");
        for(let i = 0; i<checkboxes.length; i++){
            checkboxes[i].checked = false;
        }

        document.getElementById("extras").value = "";

        //Adds another sign up in the tfoot if under max capacity
        console.log(document.querySelector("#" + tableid + "Signup tbody").querySelectorAll("tr").length);
        console.log(window["max" + tableid]);
        if (document.querySelector("#" + tableid + "Signup tbody").querySelectorAll("tr").length < window["max" + tableid]) {
            const newRow = document.createElement('tr');    
            newRow.className = "signUp";
            
            const newData = document.createElement("td");
            newData.style.textAlign = "right";
            newData.setAttribute('colspan', 4);

            //Maintains alternating colors in table
            if (document.querySelector("#" + tableid + "Signup tbody").querySelectorAll("tr").length % 2 == 1) {
                newData.style.backgroundColor = "rgb(112, 191, 255)";
            } else {
                newData.style.backgroundColor = "rgb(163, 214, 255)";
            }

            const newButton = document.createElement("button");
            newButton.className = "signUpButton";
            newButton.innerHTML = "Sign Up";
            newButton.value = tableid;
            
            newData.appendChild(newButton);
            newRow.appendChild(newData);
            document.querySelector("#" + tableid + "Signup tfoot").appendChild(newRow);
            
            //Updates available slots number

            /*console.log(window["max" + tableid]);
            console.log(document.querySelector("#" + tableid + "Signup tbody").querySelectorAll("tr"));
            */
            document.querySelector("#" + tableid + "Signup th").innerHTML = tableText + " (" + (window["max" + tableid]-document.querySelector("#" + tableid + "Signup tbody").querySelectorAll("tr").length) + "/" + window["max" + tableid] + " available slots)";

            newButton.addEventListener("click", function(){
                showInputs();
                tableid = newButton.value;
            }); /*Recursion to keep adding the sign up button in the footer until table hits max length*/
        } else if (document.querySelector("#" + tableid + "Signup tbody").querySelectorAll("tr").length == window["max" + tableid]) {
            //Updates available slots number
            document.querySelector("#" + tableid + "Signup th").innerHTML = tableText + " (All slots filled)";
        }
        close_button.addEventListener("click", function() {
            deleteRow(newtr,newtr.parentElement.parentElement.id);
            console.log("deleting");
        });
    }
}

function checkInputs(){
    if (document.getElementById("nameInput").value !== "" && document.getElementById("dishNameInput").value !== "" && document.getElementById("emailInput").value !== "") {
        document.getElementById("confirm").innerHTML = "Confirm";
        document.getElementById("confirm").style.color = "black";
        document.getElementById("confirm").style.fontWeight = "normal";
    }

    if(document.getElementById("nameInput").value !== ""){
        document.getElementById("nameInput").style.border = "1px solid black";
    }
    if(document.getElementById("dishNameInput").value !== ""){
        document.getElementById("dishNameInput").style.border = "1px solid black";
    }
    if(document.getElementById("emailInput").value !== ""){
        document.getElementById("emailInput").style.border = "1px solid black";
    }
}
function emailtolead() {
    
}
function showInputs(){
    document.getElementById("inputs").style.setProperty("display", "block", "important");
    document.getElementById("confirm").innerHTML = "Confirm";
    document.getElementById("confirm").style.color = "black";
    document.getElementById("confirm").style.fontWeight = "normal";
    document.getElementById("nameInput").style.border = "1px solid black";
    document.getElementById("dishNameInput").style.border = "1px solid black";
    document.getElementById("emailInput").style.border = "1px solid black";
}

function deleteRow(row,id) {
    console.log("num: " + document.querySelectorAll("#" + id + " tfoot tr").length);
    console.log("deleting 1");
    const popup = document.getElementById("deletePopup");
    popup.style.display = "block";

    document.getElementById("confirmDelete").addEventListener("click",function(){
        row.remove();
        popup.style.display = "none";
        console.log("deleting 2");
        let tableid = id.substring(0,id.indexOf("Signup"));
        document.querySelector("#" + tableid + "Signup th").innerHTML = tableText + " (" + (window["max" + tableid]-document.querySelector("#" + tableid + "Signup tbody").querySelectorAll("tr").length) + "/" + window["max" + tableid] + " available slots)";
        console.log("foot: " + document.querySelector("#" + tableid + "Signup tfoot").querySelectorAll("tr").length);
        if(document.querySelectorAll("#" + id + " tfoot tr").length == 0){
            const newRow = document.createElement('tr');
            newRow.className = "signUp";
            
            const newData = document.createElement("td");
            newData.style.textAlign = "right";
            newData.setAttribute('colspan', 4);
            const newButton = document.createElement("button");
            newButton.className = "signUpButton";
            newButton.innerHTML = "Sign Up";
            newButton.value = tableid;
            newButton.addEventListener("click", function(){
                showInputs();
                tableid = newButton.value;
            })
            
            newData.appendChild(newButton);
            newRow.appendChild(newData);
            document.querySelector("#" + tableid + "Signup tfoot").appendChild(newRow);
        }
    });

    document.getElementById("cancelDelete").addEventListener("click", function () {
        popup.style.display = "none";
        return;
    });
    
}
////////////////////////////////////////////////////////////////////////////////
//Event Listeners
////////////////////////////////////////////////////////////////////////////////
document.getElementById("confirm").addEventListener('click', function(){
    addItem();
})

/*document.getElementById("appetizerSignupButton").addEventListener("click", function(){
    showInputs();
    tableid = "appetizer";
    tableText = "Appetizers";
});

document.getElementById("dessertSignupButton").addEventListener("click", function(){
    showInputs();
    tableid = "dessert";
    tableText = "Desserts";
});*/

document.getElementById("nameInput").addEventListener("input", checkInputs);
document.getElementById("dishNameInput").addEventListener("input", checkInputs);
document.getElementById("emailInput").addEventListener("input", checkInputs);

//Escapes out of popup when 'X' or escape key pressed
document.getElementById("closeSignUp").addEventListener("click", function(){
    document.getElementById("inputs").style.setProperty("display", "none", "important");
    document.getElementById("nameInput").value = "";
    document.getElementById("dishNameInput").value = "";
    document.getElementById("emailInput").value = "";
    document.getElementById("extras").value = "";
})

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        document.getElementById("inputs").style.setProperty("display", "none", "important");
        document.getElementById("nameInput").value = "";
        document.getElementById("dishNameInput").value = "";
        document.getElementById("emailInput").value = "";
        document.getElementById("extras").value = "";
    }
  });
  document.getElementById("addTable").addEventListener("click",function(){
    let tableName = document.getElementById("tableName").value;
    let maxEntries = document.getElementById("maxEntries").value;
    addTable(tableName,maxEntries);
  })


  function addTable(category, totalSlots) {
    const section = document.getElementById("tables");
    const tableId = category.toLowerCase() + "Signup";
    const thId = category.toLowerCase() + "_th";
    const buttonId = category.toLowerCase() + "SignupButton";
    
    const variableName = "max" + category.toLowerCase();
    window[variableName] = totalSlots;

    const table = document.createElement("table");
    table.id = tableId;
    
    const thead = document.createElement("thead");
    const trHead = document.createElement("tr");
    const th = document.createElement("th");
    th.id = thId;
    th.colSpan = 4;
    th.textContent = category.substring(0,1).toUpperCase() + category.substring(1) + " " + totalSlots + "/" + totalSlots + " available slots";
    
    trHead.appendChild(th);
    thead.appendChild(trHead);
    
    const tbody = document.createElement("tbody");
    
    const tfoot = document.createElement("tfoot");
    const trFoot = document.createElement("tr");
    trFoot.classList.add("signUp");
    const td = document.createElement("td");
    td.colSpan = 4;
    const button = document.createElement("button");
    button.classList.add("signUpButton");
    button.id = buttonId;
    button.textContent = "Sign up";
    button.addEventListener("click", function(){
        showInputs();
        tableid = category;
        tableText = category.substring(0,1).toUpperCase() + category.substring(1);
    });
    
    td.appendChild(button);
    trFoot.appendChild(td);
    tfoot.appendChild(trFoot);
    
    // Append all parts to table
    table.appendChild(thead);
    table.appendChild(tbody);
    table.appendChild(tfoot);
    
    // Append table to section
    section.appendChild(document.createElement("br"));
    section.appendChild(table);
}