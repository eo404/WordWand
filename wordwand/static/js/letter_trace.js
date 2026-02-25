// ===============================
// WORDWAND TRACE ENGINE 
// ===============================

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

canvas.width = 600;
canvas.height = 400;

let drawing = false;
let strokes = [];
let currentStroke = [];
let letterMask = null;

// Get current letter from URL
let letter = window.location.pathname.split("/")[2];

// ===============================
// DRAW LETTER MASK
// ===============================

function drawLetterMask() {

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const fontSize = canvas.height * 0.95;

    ctx.font = `${fontSize}px Arial`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Filled letter for mask
    ctx.fillStyle = "#00AEEF";
    ctx.fillText(letter, centerX, centerY);

    // Save mask
    letterMask = ctx.getImageData(0, 0, canvas.width, canvas.height);

    // Guide outline
    ctx.strokeStyle = "rgba(0, 174, 239, 0.6)";
    ctx.lineWidth = 10;
    ctx.strokeText(letter, centerX, centerY);

    // 🔥 Reset drawing style for user strokes
    ctx.strokeStyle = "#ff4444";
    ctx.lineWidth = 18;
    ctx.lineCap = "round";
}

drawLetterMask();

// ===============================
// DRAWING EVENTS
// ===============================

canvas.addEventListener("mousedown", startDraw);
canvas.addEventListener("mousemove", draw);
canvas.addEventListener("mouseup", stopDraw);
canvas.addEventListener("mouseleave", stopDraw);

// Touch support
canvas.addEventListener("touchstart", startDraw);
canvas.addEventListener("touchmove", drawTouch);
canvas.addEventListener("touchend", stopDraw);

function startDraw(e) {
    drawing = true;
    currentStroke = [];

    const { x, y } = getCoords(e);
    currentStroke.push({ x, y });
}

function draw(e) {
    if (!drawing) return;

    const { x, y } = getCoords(e);

    const last = currentStroke[currentStroke.length - 1];

    ctx.beginPath();
    ctx.moveTo(last.x, last.y);
    ctx.lineTo(x, y);
    ctx.stroke();

    currentStroke.push({ x, y });
}

function drawTouch(e) {
    e.preventDefault();
    draw(e.touches[0]);
}

function stopDraw() {
    if (drawing && currentStroke.length > 0) {
        strokes.push(currentStroke);
        currentStroke = [];
    }
    drawing = false;
}

// ===============================
// GET SCALED COORDINATES
// ===============================

function getCoords(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    };
}

// ===============================
// ACCURACY CALCULATION
// ===============================

function calculateAccuracy() {

    if (!letterMask || strokes.length === 0) return 0;

    const allPoints = strokes.flat();

    let totalError = 0;
    let sampleCount = 0;

    const tolerance = 45;

    for (let y = 0; y < letterMask.height; y += 15) {
        for (let x = 0; x < letterMask.width; x += 15) {

            const idx = (y * letterMask.width + x) * 4;

            if (letterMask.data[idx + 3] > 128) {

                sampleCount++;

                let minDist = Infinity;

                allPoints.forEach(pt => {
                    const d = Math.hypot(x - pt.x, y - pt.y);
                    if (d < minDist) minDist = d;
                });

                totalError += minDist;
            }
        }
    }

    if (sampleCount === 0) return 0;

    const avgError = totalError / sampleCount;

    return Math.max(0, 1 - avgError / tolerance) * 100;
}

// ===============================
// CHECK FUNCTION
// ===============================

function checkDrawing() {

    const resultText = document.getElementById("resultText");
    const backBtn = document.getElementById("backBtn");

    if (strokes.length === 0) {
        resultText.innerText = "Draw something first 😊";
        resultText.style.color = "#ff6b6b";
        return;
    }

    const score = calculateAccuracy();

    if (score >= 70) {
        resultText.innerText = "Wow! You did it! 🌟";
        resultText.style.color = "#4CAF50";
        showStars();
    }
    else if (score >= 40) {
        resultText.innerText = "Great job! ⭐";
        resultText.style.color = "#4CAF50";
        showStars();
    }
    else {
        resultText.innerText = "Try again 😊";
        resultText.style.color = "#ff4444";
    }

    // 🔓 Show back button only after checking
    if (backBtn) {
        backBtn.style.display = "inline-block";
    }
}

// ===============================
// RETRY FUNCTION
// ===============================

function retry() {

    strokes = [];
    currentStroke = [];

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawLetterMask();

    document.getElementById("resultText").innerText = "";

    const backBtn = document.getElementById("backBtn");
    if (backBtn) {
        backBtn.style.display = "none";
    }
}

// ===============================
// GO TO ALPHABET GRID
// ===============================

function goToAlphabet() {
    window.location.href = "/alphabetgrid";
}

// ===============================
// SIMPLE STAR ANIMATION
// ===============================

function showStars() {

    const star = document.createElement("div");
    star.innerHTML = "⭐ ⭐ ⭐";
    star.style.position = "absolute";
    star.style.top = "40%";
    star.style.left = "50%";
    star.style.transform = "translate(-50%, -50%)";
    star.style.fontSize = "40px";
    star.style.animation = "fadeOut 1.5s forwards";
    star.style.pointerEvents = "none";

    document.body.appendChild(star);

    setTimeout(() => star.remove(), 1500);
}