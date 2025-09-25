document.getElementById("homePage").addEventListener("click", function () {
    const targetUrl = this.dataset.url;
    window.location.href = targetUrl;
});

// document.querySelectorAll(".signUpButton").forEach(button => {
//     button.addEventListener("click", () => {
//         const tableId = button.getAttribute("data-table-id");
//         const form = document.getElementById("signupForm");

//         // Set the form's action dynamically
//         form.action = `/signup/${tableId}`;

//         // Optionally set the hidden input (if you want to use it in backend)
//         document.getElementById("table_id_hidden").value = tableId;

//         // Show the popup
//         document.getElementById("inputs").style.display = "block";
//     });
// });

const showAddTableBtn = document.getElementById("showAddTable");
if (showAddTableBtn) {
    showAddTableBtn.addEventListener("click", function () {
        console.log("entered");
        document.getElementById("tableForm").style.display = "block";
    });
}

document.getElementById("cancelAddTable").addEventListener("click",function(){
    document.getElementById("tableForm").style.display = "none";
})

// document.getElementById("closeSignUp").addEventListener('click', () => {
//     document.getElementById("inputs").style.setProperty("display", "none", "important");
// });

function showComment(id) {
    const popup = document.getElementById(`comment-popup-${id}`);
    if (popup) popup.style.display = 'block';
}

function hideComment(id) {
    const popup = document.getElementById(`comment-popup-${id}`);
    if (popup) popup.style.display = 'none';
}

document.querySelectorAll(".edit-table-button").forEach(button => {
    button.addEventListener("click", () => {
        // Show the form
        const form = document.getElementById("tableForm");
        form.style.display = "block";

        // Fill form with existing table data
        document.getElementById("formTitle").innerText = "Edit Table";
        document.getElementById("tableId").value = button.dataset.tableId;
        document.getElementById("tableName").value = button.dataset.category;
        document.getElementById("maxEntries").value = button.dataset.maxEntries;
        document.getElementById("vieworder").value = button.dataset.vieworder;
    });
});

document.getElementById("cancelAddTable").addEventListener("click", function () {
    document.getElementById("tableForm").style.display = "none";

    // Reset form
    document.getElementById("formTitle").innerText = "Add a Table";
    document.getElementById("tableId").value = "";
    document.getElementById("tableName").value = "";
    document.getElementById("maxEntries").value = "";
    document.getElementById("vieworder").value = "";
});

// document.querySelectorAll(".edit-signup-button").forEach(btn => {
//     btn.addEventListener("click", () => {
//         console.log("entered edit")
//         const signupId = btn.dataset.id;
//         const dish = btn.dataset.dish;
//         const comment = btn.dataset.comment;

//         const form = document.getElementById("editSignupForm");
//         form.action = `/signup/${btn.closest("table").dataset.signupId}`;
//         document.getElementById("dishNameInput").value = dish;
//         document.getElementById("extras").value = comment;
//         document.getElementById("event_id_hidden").value = signupId;

//         document.getElementById("table_id_hidden").disabled = true;
//         document.getElementById("inputs").style.display = "block";
//     });
// });



document.addEventListener("DOMContentLoaded", () => {
    console.log("hi");
    let deleteSignupUrl = "";
    let deleteTableUrl = "";

    // SIGNUP DELETE HANDLERS
    document.querySelectorAll(".delete-signup-button").forEach(btn => {
        btn.addEventListener("click", (e) => {
            console.log('test1')
            e.preventDefault();
            console.log('test2')
            deleteSignupUrl = btn.dataset.url;
            document.getElementById("deleteSignupPopup").style.setProperty("display", "block", "important");
        });
    });

    document.getElementById("confirmDeleteSignup").addEventListener("click", () => {
        if (deleteSignupUrl) {
            window.location.href = deleteSignupUrl;
        }
    });

    document.getElementById("cancelDeleteSignup").addEventListener("click", () => {
        document.getElementById("deleteSignupPopup").style.setProperty("display", "none", "important");
        deleteSignupUrl = "";
    });

    // TABLE DELETE HANDLERS
    document.querySelectorAll(".delete-table-button").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            deleteTableUrl = btn.dataset.url;
            document.getElementById("deleteTablePopup").style.setProperty("display", "block", "important");
        });
    });

    document.getElementById("confirmDeleteTable").addEventListener("click", () => {
        if (deleteTableUrl) {
            window.location.href = deleteTableUrl;
        }
    });

    document.getElementById("cancelDeleteTable").addEventListener("click", () => {
        document.getElementById("deleteTablePopup").style.setProperty("display", "none", "important");
        deleteTableUrl = "";
    });

    
});

const inputsDiv = document.getElementById("inputs");
const form = document.getElementById("signupForm");

const dishInput = document.getElementById("dishNameInput");
const extrasInput = document.getElementById("extras");
const tableIdInput = document.getElementById("table_id_hidden");
const signupIdInput = document.getElementById("signup_id_hidden");

// Open form for new signup
document.querySelectorAll(".signUpButton").forEach(button => {
    button.addEventListener("click", () => {
        const tableId = button.dataset.tableId;
        
        form.action = `/drsu/signup/${tableId}`; // set to signup route
        tableIdInput.value = tableId;
        signupIdInput.value = "";

        dishInput.value = "";
        extrasInput.value = "";

        inputsDiv.style.display = "block";
    });
});

// Open form for editing existing signup
document.querySelectorAll(".edit-signup-button").forEach(button => {
    button.addEventListener("click", () => {
        const signupId = button.dataset.id;
        const dish = button.dataset.dish || "";
        const comment = button.dataset.comment || "";

        form.action = `/drsu/edit_signup/${signupId}`; // set to edit route
        signupIdInput.value = signupId;
        dishInput.value = dish;
        extrasInput.value = comment;

        inputsDiv.style.display = "block";
    });
});

// Close form
document.getElementById("closeSignUp").addEventListener("click", () => {
    inputsDiv.style.display = "none";
});
