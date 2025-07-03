import os
import cv2
from flask import Flask, render_template, Response
import time
from ultralytics import YOLO

# Initialize YOLO model with the specified weights file
yolo = YOLO("yolov10s.pt")

# Function to generate colors for bounding boxes based on class number
def getColours(cls_num):
    base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    color_index = cls_num % len(base_colors)
    increments = [(1, -2, 1), (-2, 1, -1), (1, -1, 2)]
    color = [base_colors[color_index][i] + increments[color_index][i] * 
    (cls_num // len(base_colors)) % 256 for i in range(3)]
    return tuple(color)

# Create Flask app instance
app = Flask(__name__)
cam_status = "Waiting"  # Variable to track camera status

# Generator function to capture frames from the camera, run YOLO detection, and stream to client
def gen_frames():
    camera = cv2.VideoCapture(0)  # Open the default camera
    # Set camera resolution for faster processing
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    global cam_status, timer  # Use global variables for camera status and timer
    while True:
        
        
        ret, frame = camera.read()  # Read a frame from the camera
        if not ret:
            break  # If frame not read correctly, exit loop
        # Resize frame for faster processing (optional, already set camera resolution)
        # frame = cv2.resize(frame, (640, 480))
        results = yolo.track(frame, stream=True)  # Run YOLO tracking on the frame
        for result in results:
            classes_names = result.names  # Get class names from YOLO result
            for box in result.boxes:
                if box.conf[0] > 0.4:  # Only draw boxes with confidence > 0.4
                    [x1, y1, x2, y2] = box.xyxy[0]  # Get bounding box coordinates
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    cls = int(box.cls[0])  # Get class index
                    class_name = classes_names[cls]  # Get class name
                    colour = getColours(cls)  # Get color for this class
                    # Draw bounding box and label on the frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
                    cv2.putText(frame, f'{class_name} {box.conf[0]:.2f}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2)
        obj= len(result.boxes)
        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])  # Lower quality for faster streaming
        frame = buffer.tobytes()
        # Yield the frame in a format suitable for streaming via HTTP
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        cam_status = "Live"  # Update camera status while streaming
        # To further increase speed, you can add a sleep or skip frames here
        # import time; time.sleep(0.01)  # Uncomment to limit FPS
    camera.release()  # Release the camera resource
    cv2.destroyAllWindows()  # Close any OpenCV windows
    cam_status = "Stopped"  # Update camera status when done
    return cam_status, timer  # Return camera status

# Route for the home page
@app.route('/')
def home():
    return render_template(
        'index.html',
        gen_frames=gen_frames, # Pass the frame generator to the template
        cam_status=cam_status  # Pass camera status to the template
        )

# Route for the video feed stream
@app.route('/video_feed')
def video_feed():
    # Return a streaming response using the frame generator
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
cam_status = "Waiting"  # Initialize camera status
# Main entry point to run the Flask app
if __name__ == '__main__':
        app.run(debug=True)
cam_status = "Waiting"  # Set initial camera status to live