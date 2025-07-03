document.addEventListener('DOMContentLoaded', () => {
    console.log('Document loaded and ready');
document.getElementById('startButton').addEventListener('click', async () => {
    const video = document.getElementById('video');
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.play();

    // Create a writable stream to handle the video data
    const writer = new WritableStream({
        write(chunk) {
            // Handle the video chunk here
            console.log('Video chunk received:', chunk);
        }
    });

    // Use the writer to process the video stream
    const reader = stream.getVideoTracks()[0].createReader();
    function read() {
        reader.read().then(({ done, value }) => {
            if (done) {
                console.log('Stream finished');
                return;
            }
            writer.getWriter().write(value).then(() => {
                read(); // Continue reading
            });
        });
    }
    read();
});
}              );  
document.getElementById('stopButton').addEventListener('click', () => {
    const video = document.getElementById('video');
    const stream = video.srcObject;
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        console.log('Video stream stopped');
    }
});
document.getElementById('toggleButton').addEventListener('click', () => {
    const video = document.getElementById('video');
    if (video.style.display === 'none') {
        video.style.display = 'block';
        console.log('Video display enabled');
    } else {
        video.style.display = 'none';
        console.log('Video display disabled');
    }
});
document.getElementById('resetButton').addEventListener('click', () => {   
    const video = document.getElementById('video');
    video.srcObject = null;
    video.style.display = 'none';
    console.log('Video reset');
});
