window.addEventListener("scroll", function () {
    let scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
    let maxScroll = 400;

    let darkness = Math.min(scrollTop / maxScroll, 1);
    let bgColor = `rgb(${234 - (110 * darkness)}, ${234 - (104 * darkness)}, ${234 - (96 * darkness)})`;

    document.body.style.backgroundColor = bgColor;

    
    document.querySelectorAll(".binary").forEach(binary => {
        binary.style.opacity = darkness; 
    });
});
