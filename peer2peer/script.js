// script.js

const uid = self.crypto.randomUUID();

function addLogMessage() {
    console.log(`Logging for ${uid}`);
    const log_entry = document.createElement("li");
    log_entry.textContent = uid;
    const log_list = document.querySelector("#log");
    log_list.append(log_entry);
}

const uid_elem = document.querySelector("#uid");
uid_elem.textContent = uid;

const btn = document.querySelector("#fire");
btn.addEventListener("click", addLogMessage);

const rtc_config = {
    iceServers: [{ urls: "stun:stun.my-stun-server.tld" }],
    //   alwaysNegotiateDataChannels: true
};

function receiveData(event) {
    console.log(`Received ${event.data}`);
}

const pc = new RTCPeerConnection(rtc_config);
const dc = pc.createDataChannel("pictopair");
dc.addEventListener("open", (event) => {
    console.log("dataChannel ready.", event);
});
dc.addEventListener("close", (event) => {
    console.log("dataChannel closed.", event)
});
dc.addEventListener("message", receiveData);
