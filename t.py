# import the necessary packages

import time
import cv2
import gi.repository.Gst as Gst
import curses

# Загрузка видео
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Получение первого кадра
ok, frame = cap.read()
if not ok:
    print('Cannot read video file')
    exit()

# Выбор области для трекинга
#bbox = cv2.selectROI(frame, False)

# Инициализация CSRT трекера
#tracker = cv2.TrackerCSRT_create()
#tracker.init(frame, bbox)
bbox = None
# Инициализация curses
stdscr = curses.initscr()
curses.noecho()
stdscr.keypad(True)
# Устанавливаем таймаут ввода в 0, чтобы программа не ожидала ввода с клавиатуры
stdscr.timeout(0)


# Создаем объект GStreamer пайплайна
pipeline = "appsrc name=source ! videoconvert ! fbdevsink"
pipe = Gst.parse_launch(pipeline)
source = pipe.get_by_name("source")
source_caps = Gst.Caps.from_string("video/x-raw,format=BGR,width={},height={}".format(int(320), int(240)))
source.set_property("caps", source_caps)
sink = pipe.get_by_name("fbdevsink")
# Запускаем пайплайн
pipe.set_state(Gst.State.PLAYING)

# Центральные координаты и размер области интереса
center_x = 320 // 2
center_y = 240 // 2
roi_size = 30

# Вычисление координат углов ROI
x1 = int(center_x - roi_size / 2)
y1 = int(center_y - roi_size / 2)
x2 = int(center_x + roi_size / 2)
y2 = int(center_y + roi_size / 2)


while True:
    # Получение следующего кадра
    ok, frame = cap.read()
    if not ok:
        break


    # check to see if we are currently tracking an object
    if bbox is not None:
        # grab the new bounding box coordinates of the object
        (success, box) = tracker.update(frame)
        # check to see if the tracking was a success
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                (0, 255, 0), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 1)
 

            


    # show the output frame
    # Передаем кадр в пайплайн GStreamer
    buf = Gst.Buffer.new_wrapped(frame.tobytes())
    source.emit("push-buffer", buf)

    #cv2.imshow("Frame", frame)

    stdscr.refresh()
    c = stdscr.getch()

    if c == ord(" "):
        # select the bounding box of the object we want to track (make
        # sure you press ENTER or SPACE after selecting the ROI)
        #initBB = cv2.selectROI("Frame", frame, fromCenter=False,
        #    showCrosshair=True)
        bbox = (x1, y1, roi_size, roi_size)
        tracker = cv2.TrackerCSRT_create()
        tracker.init(frame, bbox)


    # if the `q` key was pressed, break from the loop
    elif c == ord("q"):
        break

    if c == ord("w"):
        break
# if we are using a webcam, release the pointer

else:
    vs.release()
curses.endwin()


