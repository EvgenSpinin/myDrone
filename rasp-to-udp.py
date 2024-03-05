import cv2
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

# Инициализация GStreamer
Gst.init(None)

# Создаем объект захвата видео с помощью OpenCV
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Создаем объект GStreamer пайплайна
pipeline = "appsrc name=source ! videoconvert ! x264enc ! h264parse ! rtph264pay pt=96 ! udpsink host=192.168.0.110 port=5600"
pipe = Gst.parse_launch(pipeline)
source = pipe.get_by_name("source")
source_caps = Gst.Caps.from_string("video/x-raw,format=BGR,width={},height={}".format(int(320), int(240)))
source.set_property("caps", source_caps)

# Запускаем пайплайн
pipe.set_state(Gst.State.PLAYING)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Передаем кадр в пайплайн GStreamer
    buf = Gst.Buffer.new_wrapped(frame.tobytes())
    source.emit("push-buffer", buf)

cap.release()