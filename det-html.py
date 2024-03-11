# ПЕРЕД запуском создаем папку template и помещаем туда содержимое html-страницы
from flask import Flask, render_template, Response
import cv2
import argparse

app = Flask(__name__)

# camera = cv2.VideoCapture(0)  # Веб-камера
camera = cv2.VideoCapture(0)  # RTSP-поток
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Ширина кадра
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Высота кадра

#for DEtection
classNames = []
classFile = "/home/pi/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pi/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    #print(classIds,bbox)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=1)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,0.35,(0,255,0),1)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+70,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,0.35,(0,255,0),1)

    return img,objectInfo


def getFramesGenerator():
    """Генератор кадров для вывода на веб-страницу."""
    while True:
        success, frame = camera.read()  # Получаем кадр с камеры
        if not success:
            continue  # Пропустить кадр, если не удалось получить
        frame = cv2.rotate(frame, cv2.ROTATE_180)


        #success, img = cap.read()
        result, objectInfo = getObjects(frame,0.45,0.2)
        
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
