# ПЕРЕД запуском создаем папку template и помещаем туда содержимое html-страницы
from flask import Flask, render_template, Response
import cv2
import argparse
import curses

app = Flask(__name__)

# camera = cv2.VideoCapture(0)  # Веб-камера
camera = cv2.VideoCapture(0)  # RTSP-поток
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Ширина кадра
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Высота кадра

# Получение первого кадра
ok, frame = camera.read()
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

# Центральные координаты и размер области интереса
center_x = 320 // 2
center_y = 240 // 2
roi_size = 30

# Вычисление координат углов ROI
x1 = int(center_x - roi_size / 2)
y1 = int(center_y - roi_size / 2)
x2 = int(center_x + roi_size / 2)
y2 = int(center_y + roi_size / 2)



def getFramesGenerator():
    """Генератор кадров для вывода на веб-страницу."""
    bbox = None
    while True:
        success, frame = camera.read()  # Получаем кадр с камеры
        if not success:
            continue  # Пропустить кадр, если не удалось получить
        frame = cv2.rotate(frame, cv2.ROTATE_180)
            # check to see if we are currently tracking an object
        if bbox is not None:
            # grab the new bounding box coordinates of the object
            (success, box) = tracker.update(frame)
            # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                    (0, 255, 0), 1)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (50, 0, 0), 1)

        cv2.putText(frame, 'mot: {}', (8, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (50, 0, 0), 1, cv2.LINE_AA)  # добавляем поверх кадра текст



        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

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

@app.route('/video_feed')
def video_feed():
    """Генерирует и отправляет изображения с камеры."""
    return Response(getFramesGenerator(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Крутит html-страницу."""
    return render_template('index.html')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, help="Running port")
    parser.add_argument("-i", "--ip", type=str, default='192.168.0.112', help="Ip address")
    args = parser.parse_args()

    app.run(debug=False, host=args.ip, port=args.port)  # Запускаем Flask-приложение

    # Освобождаем ресурсы камеры после завершения
    camera.release()
    curses.endwin()
