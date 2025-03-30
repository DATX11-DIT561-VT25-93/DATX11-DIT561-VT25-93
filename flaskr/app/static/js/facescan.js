document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("webcam");
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");
    const captureButton = document.querySelector("button");

    // Access the webcam
    async function startWebcam() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
        } catch (err) {
            console.error("Error accessing webcam:", err);
        }
    }

    // Capture a frame from the video
    function captureFrame() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to base64 for temporary storage
        const imageData = canvas.toDataURL("image/png");
        console.log("Captured Image:", imageData);
    }

    // Start webcam automatically on page load
    startWebcam();

    // Capture image when button is clicked
    captureButton.addEventListener("click", captureFrame);
});
