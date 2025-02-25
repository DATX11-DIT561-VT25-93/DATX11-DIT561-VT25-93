const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

async function startWebcam() {
    try {
        console.log('Trying to access webcam...');
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (error) {
        console.error("Error accessing webcam:", error);
    }
}

function captureAndSendFrame() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg'); // Convert to Base64

    fetch('/register-face-detection', {  // Send to Flask backend
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

    setTimeout(captureAndSendFrame, 5000); // Capture every 5000ms
}

document.getElementById('startButton').addEventListener('click', () => {
    document.getElementById('webcam').style.display = 'block';
    document.getElementById('startButton').style.display = 'none';

    startWebcam();
    setTimeout(captureAndSendFrame, 1000); // Start streaming after 1s
});
