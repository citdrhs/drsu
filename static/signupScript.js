document.getElementById("homePage").addEventListener("click", function () {
    const targetUrl = this.dataset.url;
    window.location.href = targetUrl;
});

document.querySelectorAll(".signUpButton").forEach(button => {
    button.addEventListener("click", () => {
        const tableId = button.getAttribute("data-table-id");
        const form = document.getElementById("signupForm");

        // Set the form's action dynamically
        form.action = `/signup/${tableId}`;

        // Optionally set the hidden input (if you want to use it in backend)
        document.getElementById("table_id_hidden").value = tableId;

        // Show the popup
        document.getElementById("inputs").style.display = "block";
    });
});

document.getElementById("showAddTable").addEventListener("click",function(){
    console.log("entered");
    document.getElementById("tableForm").style.display = "block";
})

document.getElementById("cancelAddTable").addEventListener("click",function(){
    document.getElementById("tableForm").style.display = "none";
})

document.getElementById("closeSignUp").addEventListener('click', () => {
    document.getElementById("inputs").style.setProperty("display", "none", "important");
});

function showComment(id) {
    const popup = document.getElementById(`comment-popup-${id}`);
    if (popup) popup.style.display = 'block';
}

function hideComment(id) {
    const popup = document.getElementById(`comment-popup-${id}`);
    if (popup) popup.style.display = 'none';
}

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
