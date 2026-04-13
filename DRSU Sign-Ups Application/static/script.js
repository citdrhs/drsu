document.getElementById("homePage").addEventListener("click", function () {
    const targetUrl = this.dataset.url;
    window.location.href = targetUrl;
});

// Dropdown menu handling
const optionBarTrigger = document.getElementById("optionBarTrigger");
const dropdown = document.getElementById("dropdown");

if (optionBarTrigger && dropdown) {
    let hideTimeout;

    const showDropdown = () => {
        clearTimeout(hideTimeout);
        optionBarTrigger.classList.add("dropdown-active");
        dropdown.classList.add("dropdown-active");
    };

    const hideDropdown = () => {
        hideTimeout = setTimeout(() => {
            optionBarTrigger.classList.remove("dropdown-active");
            dropdown.classList.remove("dropdown-active");
        }, 150);
    };

    optionBarTrigger.addEventListener("mouseenter", showDropdown);
    optionBarTrigger.addEventListener("mouseleave", hideDropdown);
    
    dropdown.addEventListener("mouseenter", showDropdown);
    dropdown.addEventListener("mouseleave", hideDropdown);
}