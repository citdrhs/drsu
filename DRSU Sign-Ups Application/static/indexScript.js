document.addEventListener('DOMContentLoaded', function () {
    const openButton = document.querySelector('.big-button');
    const closeButton = document.getElementById('closeAddEvent');
    const addEventInput = document.getElementById('addEventInput');
    const eventForm = document.querySelector('.eventForm');
    
    // Create modal backdrop if it doesn't exist
    let modalBackdrop = document.getElementById('modalBackdrop');
    if (!modalBackdrop) {
        modalBackdrop = document.createElement('div');
        modalBackdrop.id = 'modalBackdrop';
        document.body.appendChild(modalBackdrop);
    }

    function openModal() {
        addEventInput.classList.add('active');
        modalBackdrop.classList.add('active');
    }

    function closeModal() {
        addEventInput.classList.remove('active');
        modalBackdrop.classList.remove('active');
        eventForm.reset();
        document.getElementById("addEventHeader").textContent = "Add Event";
        document.getElementById("eventSubmitBtn").textContent = "Create Event";
        document.getElementById("event_id_hidden").value = '';
    }

    // Open form
    if (openButton) {
        openButton.addEventListener('click', openModal);
    }

    // Close form
    closeButton.addEventListener('click', closeModal);
    
    // Close modal when clicking backdrop
    modalBackdrop.addEventListener('click', closeModal);
    
    // Prevent closing when clicking on the modal itself
    addEventInput.addEventListener('click', (e) => {
        e.stopPropagation();
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
    document.getElementById("eventSubmitBtn").textContent = "Save";
    
    // Open modal using the new system
    const addEventInput = document.getElementById('addEventInput');
    const modalBackdrop = document.getElementById('modalBackdrop');
    addEventInput.classList.add('active');
    modalBackdrop.classList.add('active');
}
