document.addEventListener('DOMContentLoaded', function () {
    const openButton = document.querySelector('.big-button');
    const closeButton = document.getElementById('closeAddEvent');
    const addEventInput = document.getElementById('addEventInput');
    const eventForm = document.querySelector('.eventForm');

    // Hide the form initially
    addEventInput.style.display = 'none';

    // Open form
    openButton.addEventListener('click', () => {
        addEventInput.style.display = 'block';
    });

    // Close form and reset
    closeButton.addEventListener('click', () => {
        addEventInput.style.display = 'none';
        eventForm.reset();
    });
});
function editEvent(id, name, date, start, end, location, contact, note) {
    document.getElementById("event_id_hidden").value = id;
    document.getElementById("eventName").value = name;
    document.getElementById("eventDate").value = date;
    document.getElementById("startTime").value = start;
    document.getElementById("endTime").value = end;
    document.getElementById("location").value = location;
    document.getElementById("contactEmail").value = contact;
    document.getElementById("note").value = note;

    console.log(date);

    document.getElementById("addEventHeader").textContent = "Edit Event";
    document.querySelector("#addEventInput").style.display = "block";
}
