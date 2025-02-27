const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const initialDelay = 1000; // Time (in ms) before webcam starts capturing and sending frames
const newFrameDelay = 5000; // Time (in ms) before a new frame is captured and sent

async function startWebcam() {
    try {
        console.log('Trying to access webcam...');
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (error) {
        console.error("Error accessing webcam:", error);
    }
}

function captureAndSendFrame(url) {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg'); // Convert to Base64

    fetch(url, {  // Send to Flask backend
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Response from backend, ', data);
            // Handle the response from the server here
        })
        .catch(error => {
            console.error('Error sending frame:', error);
        });

    setTimeout(() => captureAndSendFrame(url), newFrameDelay); 
}

document.querySelector(".startButton").addEventListener("click", (event) => {
    document.getElementById('webcam').style.display = 'block';
    event.target.style.display = "none";

    let url; // URL to which the frames are sent 

    if (event.target.id === "faceRegisterButton") {
        url = '/register-face-detection';
    } else {
        url = "/login-face-detection";
    }

    startWebcam();
    setTimeout(() => captureAndSendFrame(url), initialDelay);
});
