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
