// Copyright (c) 1999
// script.js
// Author: James and Adrian

const ip = "pictopair.frost.cx";
const socket = new WebSocket(`wss://${ip}`);
const canvas = document.querySelector("#canvas");
const ctx = canvas.getContext("2d");
const scale = Math.floor(canvas.offsetWidth / 220);
const erase_btn = document.querySelector("#erase");
const prompt = document.querySelector("#prompt");

let draw_x = 0;
let draw_y = 0;
let draw_op = 1;
let isDrawing = false;
let canDraw = false;

function toggleErase(event) {
    if (draw_op == 0) {
        erase_btn.textContent = "Drawing ✏️";
        draw_op = 1;
    } else {
        erase_btn.textContent = "Erasing 🧼";
        draw_op = 0;
    }
}

function receiveEvent(event) {
    const data = new Uint8ClampedArray(event.data);
    console.log("Received:", data);
    const [x1, y1, x2, y2, op, ...the_rest] = Array.from(data);
    if (op == 0 || op == 1) {
        drawLine(x1, y1, x2, y2, op);
    } else if (op == 254) {
        // Start event.
        const prompt_text = new TextDecoder().decode(Uint8ClampedArray.from(the_rest));
        console.log(`Start, prompt: ${prompt_text}`);
        prompt.textContent = prompt_text;
        clearCanvas();
        canDraw = true;
    } else if (op == 255) {
        // End event.
        console.log(`End, time over!`);
        canDraw = false;
        alert("Put down your pens!");
    } else {
        console.error("Unknown event received.", data);
    }
}

function sendEvent(x1, y1, x2, y2, op) {
    console.log(`Sending: (${x1},${y1},${x2},${y2},${op})`);
    socket.send(Uint8ClampedArray.from([x1, y1, x2, y2, op]));
    drawLine(x1, y1, x2, y2, op);
}

function drawLine(x1, y1, x2, y2, op) {
    ctx.fillStyle = op == 1 ? "black" : "white";
    const size = op == 1 ? 1 : 7;
    const x_diff = x2 - x1;
    const y_diff = y2 - y1;
    const half_size = Math.floor(size / 2);
    const steps = Math.max(Math.abs(x_diff), Math.abs(y_diff));
    for (let step = 0; step < steps; step++) {
        const x = x1 + Math.floor((step / steps) * x_diff) - half_size
        const y = y1 + Math.floor((step / steps) * y_diff) - half_size
        ctx.fillRect(x, y, size, size);
    }
}

function clearCanvas() {
    for (let i = 0; i < 80; i++) {
        drawLine(0, i, 255, i, 0);
    }
}

// event.offsetX, event.offsetY gives the (x,y) offset
// from the edge of the canvas.
function startDraw(event) {
    if (canDraw) {
        draw_x = Math.floor(event.offsetX / scale);
        draw_y = Math.floor(event.offsetY / scale);
        isDrawing = true;
    }
}

function contDraw(event) {
    if (isDrawing) {
        const new_draw_x = Math.floor(event.offsetX / scale);
        const new_draw_y = Math.floor(event.offsetY / scale);
        sendEvent(draw_x, draw_y, new_draw_x, new_draw_y, draw_op);
        draw_x = new_draw_x;
        draw_y = new_draw_y;
    }
}

function endDraw(event) {
    if (isDrawing) {
        const new_draw_x = Math.floor(event.offsetX / scale);
        const new_draw_y = Math.floor(event.offsetY / scale);
        sendEvent(draw_x, draw_y, new_draw_x, new_draw_y, draw_op);
        draw_x = 0;
        draw_y = 0;
        isDrawing = false;
    }
}

// Add the event listeners for pointer.
// Unlike mouse events these support touch screens.
canvas.addEventListener("pointerdown", startDraw);
canvas.addEventListener("pointermove", contDraw);
window.addEventListener("pointerup", endDraw);
erase_btn.addEventListener("click", toggleErase);

// Receive binary messages as ArrayBuffer objects.
socket.binaryType = "arraybuffer";

socket.addEventListener("open", () => {
    console.log("Connected to Python WebSocket server");
});

socket.addEventListener("message", receiveEvent);

socket.addEventListener("close", () => {
    console.log("Disconnected from server");
});

socket.addEventListener("error", (error) => {
    console.error("WebSocket error:", error);
});
