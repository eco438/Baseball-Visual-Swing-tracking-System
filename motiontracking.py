import argparse
import imutils
import cv2

def writing_data(filename, initial_speed, final_speed, name, totaltime):
    with open(filename, "a+") as f:
        f.write("The name of the player is "+name+"\n"+
                "The final time was "+ "{:.3f}".format(final_speed)+"\n"+
                "The total time was "+ "{:.3f}".format(totaltime)+"\n\n")

def exit_velocity(exit_time,distance):
    exit_speed = distance/exit_time
    return exit_speed

def main():
    total_frames = 0
    total_time = 0
    exit_time = 0
    initialframes = 0
    framerate = 0
    prev = (0, 0, 0, 0)
    print("Enter the name of file you want to input the data: ")
    file = input()
    print("Enter the name of the player: ")
    player_name = input()
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", type=str, help="path to input video file")
    args = vars(ap.parse_args())
    tracker = cv2.TrackerCSRT_create()
    vs = cv2.VideoCapture(args["video"])
    _, frame = vs.read()
    frame = imutils.resize(frame, width=1400, height=1300)
    (H, _) = frame.shape[:2]
    initBB = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
    inital_box = tracker.init(frame, initBB)
    writer = None
    while True:
        # grab the current frame, then handle if we are using a
        # VideoStream or VideoCapture object
        frame = vs.read()
        frame = frame[1] if args.get("video", False) else frame
        # check to see if we have reached the end of the stream
        if frame is None:
            break
        # resize the frame (so we can process it faster) and grab the
        # frame dimensions
        frame = imutils.resize(frame, width=1400, height=1300)
        (H, W) = frame.shape[:2]
        if writer is None:
            if initBB is not None:
		# store the image dimensions, initialize the video writer,
		# and construct the zeros array
	            writer = cv2.VideoWriter("result.avi",cv2.VideoWriter_fourcc('M','J','P','G'),10,(W * 2, H * 2), True)
        if initBB is not None:
            # grab the new bounding box coordinates of the object
            (success, box) = tracker.update(frame)
            # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                framerate = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
                total_frames += 1 #total frames with the ball in the video
                #finds the frame when the ball gets intially hits
                #finds the time when the bounding box in the two frames are really close
                (x, y, w, h) = box
                (x2, y2, _, _) = prev
                if(abs(y2-y) <= 1.5 and abs(x2-x) <= 10):
                    initialframes = total_frames
                prev = box
            # initialize the set of information we'll be displaying on
            # the frame
        initial_time = initialframes/framerate
        post_time = (total_frames-initialframes)/framerate
        total_time = total_frames/framerate
        info = [
            ("Success", "Yes" if success else "No"),
            ("Post Hit Time", "{:.3f}".format(post_time)),
            ("Total Time", "{:.3f}".format(total_time))
        ]
        # loop over the info tuples and draw them on our frame
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        writer.write(frame)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        # if the 'q' key is selected, we are going to quit the program
        # If the 'p' key is selected, the video will pause.
        if key == ord("q"):
            break

        if key == ord("p"):
            cv2.waitKey(0)

        if not success:
            cv2.waitKey(0)
            break

    vs.release()
    cv2.destroyAllWindows()
    initial_velocity, final_velocity = exit_velocity(initial_time, 10)
    writing_data(file, initial_velocity, post_time, player_name, total_time)
main()
