import cv2

def speed_up_video(input_path, output_path, skip_frames=5):
    # Open the input video file
    cap = cv2.VideoCapture(input_path)

    # Get the frame rate of the original video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Get video dimensions
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create a VideoWriter object to save the output
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can use 'XVID' or 'mp4v' for MP4
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0

    # Loop through the video frames
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # Write every 5th frame to the output video
        if frame_count % skip_frames == 0:
            out.write(frame)
            print(f"Writing frame {frame_count}")

        frame_count += 1

    # Release the video objects
    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    input_video = "output_video.mp4"  # Replace with your .mov video path
    output_video = "output_video_2.mp4"  # Output video path

    # Speed up the video by writing every 5th frame
    speed_up_video(input_video, output_video)
