const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

const initialDelay = 1000; // Time (in ms) before webcam starts capturing and sending frames
const newFrameDelay = 1000; // Time (in ms) before a new frame is captured and sent 
const redirectDelay = 2000; // Time (in ms) before a verified user is redirected to the account page

const successMsgLogin = 'Successful login'
const successMsgRegister = 'Successful registration'

async function startWebcam() {
    try {
        console.log('Trying to access webcam...');
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (error) {
        console.error("Error accessing webcam:", error);
    }
}

function captureAndSendFrame(url, email) {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg'); // Convert to Base64

    fetch(url, {  // Send to Flask backend
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData, email: email })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Response from backend, ', data);

            if (data.message === successMsgLogin || data.message === successMsgRegister) { // If face is detected and new_image_data is present in the response
                const img = new Image();
                img.src = 'data:image/jpeg;base64,' + data.new_image_data; // Base64 string prepended with data URI scheme

                // When image is loaded, draw it on the canvas
                img.onload = function() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                };
                
                setTimeout(() => window.location.href = data.redirect, redirectDelay);
            } else { // Handle case where no face is detected
                console.log('No face detected.');
                setTimeout(() => captureAndSendFrame(url, email), newFrameDelay);
            }
        })
        .catch(error => {
            console.error('Error sending frame:', error);
        });
}

const startBtn = document.querySelector(".startButton");

startBtn.addEventListener("click", (event) => {
    let email = document.getElementById("email").value.trim();

    if (!email) {
        alert("Please enter an email before proceeding.");
        return;  // Stop execution if the input is empty
    }

    document.getElementById('container').style.display = 'block';
    event.target.style.display = "none";

    let url = event.target.id; // URL (determined by button id) to which the frames are sent 

    startWebcam();
    setTimeout(() => captureAndSendFrame(url, email), initialDelay);
});