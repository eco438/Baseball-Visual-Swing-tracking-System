import argparse
import imutils
import cv2
from scipy.spatial import distance as dist
import math

def writing_data(filename, name, Exit_Velocity):
    with open(filename, "a+") as f:
        f.write("The name of the player is "+name+"\n"+
                "The exit velocity of the ball is "+ "{:.3f}".format(Exit_Velocity)+"\n")


def main():
    total_frames = 0
    total_time = 0
    initialframes = 0
    framerate = 0
    prevcenter = (0,0)
    array = [0]
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
    # frame = imutils.resize(frame, width=1400, height=1300)
    (H, _) = frame.shape[:2]
    initBB = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
    inital_box = tracker.init(frame, initBB)
    writer = None
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
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
        #frame = imutils.resize(frame, width=1400, height=1300)
        (H, W) = frame.shape[:2]
        width = int(vs.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
        height = int(vs.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5) 
        if writer is None:
	        writer = cv2.VideoWriter("result.avi",fourcc,20,(width, height))
        if initBB is not None:
            # grab the new bounding box coordinates of the object
            (success, box) = tracker.update(frame)
            # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                framerate = int(vs.get(cv2.CAP_PROP_FPS))
                total_frames += 1 #total frames with the ball in the video
                #finds the frame when the ball gets intially hits
                #finds the time when the bounding box in the two frames are really close
                (x, y, w, h) = box
                center =  ((x +w)/2 ,(y + h)/2) 
                (x_distance,y_distance) = center
                (x2_distance,y2_distance) = prevcenter
                if(x2_distance!= 0):
                    if(x_distance> x2_distance):
                        X_value = (x_distance-x2_distance)
                        Y_value = (y_distance-y2_distance)                      
                        dist = math.sqrt((X_value*0.304)**2 + (Y_value*0.304)**2  )
                        velocity = (dist/(1/framerate))
                        array.append(velocity)
                prevcenter = center   
        total_time = total_frames/framerate
        Exit_velocity = max(array)
        info = [
            ("Name", player_name),
            ("Exit Velocity", "{:.3f}".format(Exit_velocity)),
            ("Total Time", "{:.3f}".format(total_time))
        ]
        # loop over the info tuples and draw them on our frame
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 50)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
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
    writer.release()
    cv2.destroyAllWindows()
main()
