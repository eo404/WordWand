// Speak when hovering over buttons or cards
document.querySelectorAll(".speak").forEach(el => {
    el.addEventListener("mouseenter", () => {
        speak(el.dataset.text);
    });
});

document.getElementById("mascot").addEventListener("click", () => {
    speak("Hello! Let's learn some new words today!");
});

function speak(text) {
    fetch("/tts/speak/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ text: text })
    });
}

// CSRF helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
