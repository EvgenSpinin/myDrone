# ПЕРЕД запуском создаем папку template паку с джаваскриптом  и помещаем туда содержимое html-страницы
from flask import Flask, render_template, Response, request
import cv2
import argparse
import time

app = Flask(__name__)

controlX, controlY = 0, 0  # глобальные переменные положения джойстика с web-страницы

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
    x = 0
    y = 0
    cx = 0
    cy = 0
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
                cx = (x + w)/2 #center ROI
                cy = (y + h)/2

                cv2.line(frame, (cx, 0), (cx, 240), (0, 5, 0), 1)  # рисуем л>
                cv2.line(frame, (0, cy), (320, cy), (0, 5, 0), 1)  # линия по>


        cv2.rectangle(frame, (x1, y1), (x2, y2), (50, 0, 0), 1)

        cv2.putText(frame, 'mot: X{}'.format(controlY), (8, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (50, 0, 0), 1, cv2.LINE_AA)  # добавляем поверх кадра текст

 
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


        if controlY  <  -0.5:
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

@app.route('/control')
def control():
    """ Пришел запрос на управления роботом """
    global controlX, controlY
    controlX, controlY = float(request.args.get('x')) / 100.0, float(request.args.get('y')) / 100.0
    return '', 200, {'Content-Type': 'text/plain'}
    sleep.time (1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, help="Running port")
    parser.add_argument("-i", "--ip", type=str, default='192.168.0.112', help="Ip address")
    args = parser.parse_args()

    app.run(debug=False, host=args.ip, port=args.port)  # Запускаем Flask-приложение

    # Освобождаем ресурсы камеры после завершения
    camera.release()
