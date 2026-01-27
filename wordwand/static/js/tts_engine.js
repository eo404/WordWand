// WordWand – Ultra Stable Highlight + Popup Engine

let utterance = null;

// DOM Elements
const container = document.getElementById("text-container");
const popup = document.getElementById("word-popup");
const popupWord = document.getElementById("popup-word");
const letterBox = document.getElementById("letter-box");

// =======================
// RENDER TEXT
// =======================
function renderText() {
    if (!OCR_TEXT || OCR_TEXT.trim().length === 0) return;

    container.innerHTML = "";
    const words = OCR_TEXT.split(/\s+/);

    words.forEach((word, index) => {
        // Remove punctuation for checking against lists
        const clean = word.replace(/[^\w]/g, "").toLowerCase();

        const span = document.createElement("span");
        span.className = "word";
        span.textContent = word;
        span.setAttribute("data-index", index);

        if (HARD_WORDS.includes(clean)) {
            span.classList.add("hard-word");
            // Attach the click event directly here
            span.onclick = (e) => {
                e.stopPropagation();
                openPopup(clean);
            };
        }

        container.appendChild(span);
        container.appendChild(document.createTextNode(" "));
    });
}

// =================================================
// UPDATED POPUP ENGINE
// =================================================
function openPopup(word) {
    console.log("Attempting to open popup for:", word);

    // Ensure we have syllable data for this word
    const syllableData = SYLLABLES[word.toLowerCase()];

    if (!syllableData) {
        console.warn("No syllable data found for:", word);
        return;
    }

    popupWord.textContent = word.toUpperCase();
    letterBox.innerHTML = "";

    // Split by hyphens from your Python split_into_syllables function
    const syllables = syllableData.includes("-") ? syllableData.split("-") : [syllableData];

    syllables.forEach(syl => {
        const box = document.createElement("div");
        box.className = "syllable-box"; // Use the box style from your CSS
        box.textContent = syl;

        box.onclick = () => {
            const u = new SpeechSynthesisUtterance(syl);
            u.rate = 0.6;
            speechSynthesis.speak(u);
        };

        letterBox.appendChild(box);
    });

    // Remove the 'hidden' class to show the popup
    popup.classList.remove("hidden");
}

// =======================
// READ NORMAL
// =======================
function readNormal() {
    speakText(1.0);
}

// =======================
// READ SLOW
// =======================
function readSlow() {
    speakText(0.6);
}

// =======================
// SPEAK + HIGHLIGHT (TIMER BASED)
// =======================
function speakText(rate) {
    stopSpeech();

    const spans = document.querySelectorAll(".word");
    if (spans.length === 0) return;

    utterance = new SpeechSynthesisUtterance(OCR_TEXT);
    utterance.rate = rate;

    utterance.onboundary = (event) => {
        if (event.name === 'word') {
            // Get text from start to current word boundary
            const textUpToBoundary = OCR_TEXT.substring(0, event.charIndex);

            // Count how many words are in that substring
            // Filter(Boolean) handles cases with multiple spaces
            const wordIndex = textUpToBoundary.trim().split(/\s+/).filter(Boolean).length;

            // Clear and apply highlight
            spans.forEach(s => s.classList.remove("highlight"));
            const currentSpan = document.querySelector(`.word[data-index="${wordIndex}"]`);

            if (currentSpan) {
                currentSpan.classList.add("highlight");
                currentSpan.scrollIntoView({ behavior: "smooth", block: "center" });
            }
        }
    };

    utterance.onend = () => {
        spans.forEach(s => s.classList.remove("highlight"));
    };

    speechSynthesis.speak(utterance);
}

// =======================
// STOP SPEECH
// =======================
function stopSpeech() {
    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
    }

    document.querySelectorAll(".word").forEach(w => w.classList.remove("highlight"));
}

// ================= POPUP + SYLLABLE ANIMATION SYSTEM =================

let lastPopupWord = null;

/* ----------- Simple syllable splitter (kid friendly) ----------- */
function splitIntoSyllables(word) {
    word = word.toLowerCase();
    const vowels = "aeiouy";
    let syllables = [];
    let current = "";

    for (let i = 0; i < word.length; i++) {
        current += word[i];

        if (
            vowels.includes(word[i]) &&
            (i === word.length - 1 || !vowels.includes(word[i + 1]))
        ) {
            syllables.push(current);
            current = "";
        }
    }

    if (current.length) syllables.push(current);

    return syllables;
}

/* ----------- Open popup when hard word clicked ----------- */
function openPopup(word) {
    lastPopupWord = word;

    const popup = document.getElementById("word-popup");
    const title = document.getElementById("popup-word");
    const box = document.getElementById("letter-box");

    title.textContent = word.toUpperCase();
    box.innerHTML = "";

    const syllables = splitIntoSyllables(word);

    syllables.forEach((syllable, index) => {
        const span = document.createElement("span");
        span.className = "syllable-box";
        span.textContent = syllable;
        span.style.animationDelay = `${index * 0.4}s`;
        box.appendChild(span);
    });

    popup.classList.remove("hidden");

    speakWordSlow(word);
}

/* ----------- Repeat animation + sound when Hear Again clicked ----------- */
function speakPopupWord() {
    if (!lastPopupWord) return;

    const box = document.getElementById("letter-box");
    box.innerHTML = "";

    const syllables = splitIntoSyllables(lastPopupWord);

    syllables.forEach((syllable, index) => {
        const span = document.createElement("span");
        span.className = "syllable-box";
        span.textContent = syllable;
        span.style.animationDelay = `${index * 0.4}s`;
        box.appendChild(span);
    });

    speakWordSlow(lastPopupWord);
}

/* ----------- Speak slowly (for kids) ----------- */
function speakWordSlow(word) {
    const utterance = new SpeechSynthesisUtterance(word);
    utterance.rate = 0.6;
    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
}

/* ----------- Close popup ----------- */
function closePopup() {
    document.getElementById("word-popup").classList.add("hidden");
}


// =======================
// INIT
// =======================
window.onload = function () {
    console.log("OCR_TEXT:", OCR_TEXT);
    console.log("HARD_WORDS:", HARD_WORDS);
    console.log("SYLLABLES:", SYLLABLES);

    renderText();
};
