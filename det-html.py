# ПЕРЕД запуском создаем папку template и помещаем туда содержимое html-страницы
from flask import Flask, render_template, Response
import cv2
import argparse

app = Flask(__name__)

# camera = cv2.VideoCapture(0)  # Веб-камера
camera = cv2.VideoCapture(0)  # RTSP-поток
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Ширина кадра
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Высота кадра

def getFramesGenerator():
    """Генератор кадров для вывода на веб-страницу."""
    while True:
        success, frame = camera.read()  # Получаем кадр с камеры
        if not success:
            continue  # Пропустить кадр, если не удалось получить
        frame = cv2.rotate(frame, cv2.ROTATE_180)
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, help="Running port")
    parser.add_argument("-i", "--ip", type=str, default='192.168.0.112', help="Ip address")
    args = parser.parse_args()

    app.run(debug=False, host=args.ip, port=args.port)  # Запускаем Flask-приложение

    # Освобождаем ресурсы камеры после завершения
    camera.release()
