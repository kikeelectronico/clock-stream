from vidgear.gears import WriteGear
from vidgear.gears import CamGear
import cv2
import time
import os
import datetime

ENVIROMENT = os.environ.get("ENVIROMENT", "develop")
YOUTUBE_STREAM_KEY = os.environ.get("YOUTUBE_STREAM_KEY", "")

cap = cv2.VideoCapture("video_loop.mp4")

output_params = {
    "-clones": ["-f", "lavfi", "-i", "anullsrc"],
    "-vcodec": "libx264",
    "-preset": "medium",
    "-b:v": "4500k",
    "-bufsize": "512k",
    "-pix_fmt": "yuv420p",
    "-f": "flv",
}

writer = WriteGear(
    output="rtmp://a.rtmp.youtube.com/live2/{}".format(YOUTUBE_STREAM_KEY),
    logging=False,
    **output_params
)

def getTime():
    e = datetime.datetime.now()
    hour = str(e.hour) if e.hour > 9 else "0" + str(e.hour)
    minute = str(e.minute) if e.minute > 9 else "0" + str(e.minute)
    second = str(e.second) if e.second > 9 else "0" + str(e.second)
    time_string = hour + ":" + minute + ":" + second
    return time_string
    
def writeText(frame, text):
  font_face = cv2.FONT_HERSHEY_PLAIN
  scale = 10
  color = (255, 255, 255)
  thickness = 8
  textsize, _ = cv2.getTextSize(text, font_face, scale, thickness)
  frame_height, frame_width, channels = frame.shape
  textX = round((frame_width - textsize[0]) / 2)
  textY = round((frame_height + textsize[1]) / 2)
  cv2.putText(frame, text, (textX, textY), font_face, scale, color, thickness, cv2.LINE_AA)
   
def addOverlay(frame):
    alpha = 0.2
    color = (0, 0, 0)
    overlay = frame.copy()
    frame_height, frame_width, _ = frame.shape
    cv2.rectangle(overlay, (0,0), (frame_width, frame_height), color, -1)
    new_frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    return new_frame

last_frame = None

while cap.isOpened():
    ret,frame = cap.read()
    if ret:
        frame_time_start = time.time()
        new_frame = addOverlay(frame)
        time_string = getTime()
        writeText(new_frame, time_string)
        last_frame = new_frame
        if ENVIROMENT == "production":
            writer.write(new_frame)
        else:
            show_frame = cv2.resize(new_frame, (960, 540))
            cv2.imshow("output", show_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        wait_time = (1/26) - (time.time() - frame_time_start)
        if wait_time < 0:
            wait_time = 0.001
        time.sleep(wait_time)
    else:
        if ENVIROMENT == "production":
            writer.write(last_frame)
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
    
cap.release()
writer.close()