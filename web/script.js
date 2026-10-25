// Copyright (c) 1999
// script.js
// Author: James and Adrian

const ip = "pictopair.frost.cx";
const socket = new WebSocket(`wss://${ip}`);
const canvas = document.querySelector("#canvas");
const ctx = canvas.getContext("2d");
const scale = window.getComputedStyle(document.body).getPropertyValue("--scale");
const erase_btn = document.querySelector("#erase");

let draw_x = 0;
let draw_y = 0;
let draw_op = 1;
let isDrawing = false;

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
    const data = new Uint8Array(event.data);
    console.log("Received:", data);
    const [x1, y1, x2, y2, op] = Array.from(data);
    drawLine(x1, y1, x2, y2, op);
}

function sendEvent(x1, y1, x2, y2, op) {
    console.log(`Sending: (${x1},${y1},${x2},${y2},${op})`);
    socket.send(Uint8Array.from([x1, y1, x2, y2, op]));
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

// event.offsetX, event.offsetY gives the (x,y) offset
// from the edge of the canvas.
function startDraw(event) {
    console.log(`Mouse button ${event.button}`);
    draw_x = Math.floor(event.offsetX / scale);
    draw_y = Math.floor(event.offsetY / scale);
    isDrawing = true;
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

// Add the event listeners for mousedown, mousemove, and mouseup.
canvas.addEventListener("mousedown", startDraw);
canvas.addEventListener("mousemove", contDraw);
window.addEventListener("mouseup", endDraw);
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
