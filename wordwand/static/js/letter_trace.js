const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

canvas.width = 600;
canvas.height = 400;

let drawing = false;
let strokes = 0;

canvas.addEventListener("mousedown", () => {
    drawing = true;
    strokes++;
});

canvas.addEventListener("mouseup", () => drawing = false);

canvas.addEventListener("mousemove", draw);

function draw(e) {
    if (!drawing) return;

    const rect = canvas.getBoundingClientRect();

    ctx.lineWidth = 8;
    ctx.lineCap = "round";
    ctx.strokeStyle = "red";

    ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
}

function checkDrawing() {
    let expected = 3;  // for A

    if (strokes === expected) {
        showSuccess();
    } else {
        document.getElementById("resultText")
            .innerText = `Used ${strokes} of ${expected} strokes — try again`;
    }
}

function retry() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    strokes = 0;
    document.getElementById("resultText").innerText = "";
}

function showSuccess() {
    document.getElementById("resultText").innerText = "Great Job!";
}