const buttons = document.querySelectorAll(".letter-btn");
const clickSound = document.getElementById("clickSound");

buttons.forEach(btn => {
    btn.addEventListener("click", () => {
        const letter = btn.dataset.letter;

        // Play sound
        if (clickSound) {
            clickSound.currentTime = 0;
            clickSound.play().catch(() => { });
        }

        // Button feedback
        btn.classList.add("active");

        // Redirect
        setTimeout(() => {
            window.location.href = `/letter/${letter}`;
        }, 300);
    });
});
