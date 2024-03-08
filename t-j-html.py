# ПЕРЕД запуском создаем папку template и помещаем туда содержимое html-страницы
from flask import Flask, render_template, Response, request
import cv2
import argparse
import threading

app = Flask(__name__)
controlX, controlY = 0, 0  # глобальные переменные положения джойстика с web-страницы

# camera = cv2.VideoCapture(0)  # Веб-камера
camera = cv2.VideoCapture(0)  # RTSP-поток
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Ширина кадра
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Высота кадра
text = 'OK'

def getFramesGenerator():
    """Генератор кадров для вывода на веб-страницу."""
    while True:
        success, frame = camera.read()  # Получаем кадр с камеры
        if not success:
            continue  # Пропустить кадр, если не удалось получить
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        cv2.putText(frame, 'text: {}'.format(controlY), (20, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)  # добавляем поверх кадра текст
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')



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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, help="Running port")
    parser.add_argument("-i", "--ip", type=str, default='192.168.0.112', help="Ip address")
    args = parser.parse_args()

    # Освобождаем ресурсы камеры после завершения
    camera.release()
