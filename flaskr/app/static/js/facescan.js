document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("webcam");
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");
    context.scale(-1, 1);
    context.translate(-canvas.width, 0);
    const captureButton = document.getElementById("capture-btn");
    const continueButton = document.getElementById("continue-btn");
    const retakeButton = document.getElementById("retake-btn");
    let imageData;
    let pictureHasBeenTakenBool = false;
    let stream;

    async function startWebcam() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
        } catch (err) {
            console.error("Error accessing webcam:", err);
        }
    }

    function stopWebcam() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    }

    function captureFrame() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        imageData = canvas.toDataURL("image/png");
        pictureHasBeenTakenBool = true;
        
        stopWebcam();
        
        captureButton.style.display = "none";
        continueButton.style.display = "flex";
        retakeButton.style.display = "flex";
        
        video.style.display = "none";
        canvas.style.display = "block";
    }

    function retakePicture() {
        startWebcam();
        
        video.style.display = "block";
        canvas.style.display = "none";
        
        captureButton.style.display = "flex";
        continueButton.style.display = "none";
        retakeButton.style.display = "none";
        
        pictureHasBeenTakenBool = false;
        imageData = null;
        
        context.clearRect(0, 0, canvas.width, canvas.height);
    }

    async function registerFaceScan() {
        if(!pictureHasBeenTakenBool || !imageData) { 
            alert('Please take a picture first');
            return; 
        }

        try {
            const data = {
                webcam_data: imageData
            };
            
            const response = await fetch('/register/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (response.ok) {
                window.location.href = result.next;
            } else {
                alert('Face Scan Registration failed: ' + result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while registering the face scan.');
        }
    }

    startWebcam();
    
    captureButton.addEventListener("click", captureFrame);
    retakeButton.addEventListener("click", retakePicture);
    continueButton.addEventListener("click", registerFaceScan);
});