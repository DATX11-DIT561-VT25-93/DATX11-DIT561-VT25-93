document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("webcam");
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");
    const captureButton = document.getElementById("capture-btn");
    const continueButton = document.getElementById("continue-btn");
    const retakeButton = document.getElementById("retake-btn");
    let imageData;
    let pictureHasBeenTakenBool = false;
    let stream;

    // Access the webcam
    async function startWebcam() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
        } catch (err) {
            console.error("Error accessing webcam:", err);
        }
    }

    // Stop webcam
    function stopWebcam() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    }

    // Capture a frame from the video
    function captureFrame() {
        // Set canvas dimensions to match video dimensions
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw the current video frame onto the canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to base64 for temporary storage
        imageData = canvas.toDataURL("image/png");
        pictureHasBeenTakenBool = true;
        
        // Stop the webcam
        stopWebcam();
        
        // Hide capture button and show continue/retake buttons
        captureButton.style.display = "none";
        continueButton.style.display = "flex";
        retakeButton.style.display = "flex";
        
        // Keep the canvas visible and hide the video
        video.style.display = "none";
        canvas.style.display = "block";
    }

    // Function to retake picture
    function retakePicture() {
        // Restart webcam
        startWebcam();
        
        // Show video and hide canvas
        video.style.display = "block";
        canvas.style.display = "none";
        
        // Show capture button and hide continue/retake buttons
        captureButton.style.display = "flex";
        continueButton.style.display = "none";
        retakeButton.style.display = "none";
        
        // Reset variables
        pictureHasBeenTakenBool = false;
        imageData = null;
        
        // Clear the canvas
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
            // Send data to Flask backend
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

    // Start webcam automatically on page load
    startWebcam();
    
    // Event Listeners
    captureButton.addEventListener("click", captureFrame);
    retakeButton.addEventListener("click", retakePicture);
    continueButton.addEventListener("click", registerFaceScan);
});