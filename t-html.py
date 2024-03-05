#ПЕРЕД запуском создаем папку template помещаем туда содержимое html странички
from flask import Flask, render_template, Response
import cv2
import argparse
import numpy as np

rtsp_url = 'rtsp://192.168.0.109:8554/test'
app = Flask(__name__)

camera = cv2.VideoCapture(0)  # веб камера
#camera = cv2.VideoCapture(rtsp_url)
#camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
#camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу, тут же можно поиграть с openCV"""
    while True:
        iSee = False  # флаг: был ли найден контур
        success, frame = camera.read()  # Получаем фрейм с камеры
        if success:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """ Генерируем и отправляем изображения с камеры"""
    return Response(getFramesGenerator(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """ Крутим html страницу """
    return render_template('index.html')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, help="Running port")
    parser.add_argument("-i", "--ip", type=str, default='192.168.0.105', help="Ip address")
    #parser.add_argument('-s', '--serial', type=str, default='/dev/ttyUSB0', help="Serial port")
    args = parser.parse_args()

    app.run(debug=False, host=args.ip, port=args.port)   # запускаем flask приложение

