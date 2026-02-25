document.addEventListener("DOMContentLoaded", () => {
    const startBtn = document.getElementById("startBtn");
    const whoosh = document.getElementById("whoosh");

    if (!startBtn) {
        console.error("❌ Start button not found");
        return;
    }

    // Prevent double-tap zoom on button (additional safeguard)
    startBtn.addEventListener("touchstart", (e) => {
        e.preventDefault(); // Prevents double-tap zoom
    }, { passive: false });

    startBtn.addEventListener("click", (e) => {
        e.preventDefault();

        // Disable button to prevent multiple clicks
        startBtn.disabled = true;

        // Add pressed class for animation
        startBtn.classList.add("pressed");

        // Navigate to next page after short delay
        setTimeout(() => {
            const nextUrl = startBtn.getAttribute("data-next-url") || "/alphabetgrid/";
            window.location.href = nextUrl;
        }, 500);
    });

    // Prevent zoom on form elements and interactive elements
    const interactiveElements = document.querySelectorAll('button, input, textarea, select, a');
    interactiveElements.forEach(element => {
        element.addEventListener('touchstart', (e) => {
            // This prevents double-tap zoom on these elements
        }, { passive: true });
    });

    // Prevent pinch zoom via JavaScript (additional safeguard)
    document.addEventListener('gesturestart', (e) => {
        e.preventDefault();
    });

    // Optional: Warn about disabled zoom (for debugging)
    console.log('Zoom locking enabled - page zoom is restricted');
});