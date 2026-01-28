document.addEventListener("DOMContentLoaded", () => {
    const startBtn = document.getElementById("startBtn");
    const whoosh = document.getElementById("whoosh");

    if (!startBtn) {
        console.error("❌ Start button not found");
        return;
    }

    startBtn.addEventListener("click", () => {
        startBtn.disabled = true;

        if (whoosh) {
            whoosh.currentTime = 0;
            whoosh.play().catch(() => { });
        }

        startBtn.classList.add("pressed");

        setTimeout(() => {
            window.location.href = "/alphabetgrid/";
        }, 500);
    });
});
