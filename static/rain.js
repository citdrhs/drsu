document.addEventListener("DOMContentLoaded", () => {
    function createBinary() {
        const binary = document.createElement("div");
        binary.classList.add("binary");
        binary.innerText = Math.random() > 0.5 ? "0" : "1";
        document.querySelector(".binary-container").appendChild(binary);

        const columnsLeft = [0.5, 2.5, 4.5, 6.5, 8.5]; // left of screen
        const columnsRight = [89, 91, 93, 95, 97]; // Right of screen

        // Randomly select from either left or right side
        const isLeft = Math.random() > 0.5;
        const columnPositions = isLeft ? columnsLeft : columnsRight;
        const selectedColumn = columnPositions[Math.floor(Math.random() * columnPositions.length)];

        binary.style.left = `${selectedColumn}vw`;
        binary.style.top = "-5%"; // Start slightly above the viewport

        // Set initial opacity based on scroll position
        let scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        let maxScroll = 200;
        binary.style.opacity = Math.min(scrollTop / maxScroll, 1); // Matches scroll-based opacity

        // Assign a random fall speed (between 2s and 5s)
        const duration = Math.random() * 3 + 2; // Random between 2s and 5s
        binary.style.animationDuration = `${duration}s`;

        // Remove element after animation completes
        setTimeout(() => {
            binary.remove();
        }, duration * 1000);
    }

    // Generate binary digits at intervals
    setInterval(createBinary, 50); // Adjust speed if needed
});
