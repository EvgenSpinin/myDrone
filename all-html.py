# ПЕРЕД запуском создаем папку template и помещаем туда содержимое html-страницы
from flask import Flask, render_template, Response
import cv2
import argparse

isee = False
detect = False

app = Flask(__name__)

# camera = cv2.VideoCapture(0)  # Веб-камера
camera = cv2.VideoCapture(0)  # RTSP-поток
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Ширина кадра
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Высота кадра

#for DEtection
classNames = []
classFile = "/home/pi/myDrone/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pi/myDrone/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/myDrone/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)



def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    global isee
    print(classIds,bbox)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if round(confidence*100,2) > 70:
                isee = True
                color = '255'
            else:
                isee = False
                color = '0'
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,(255,int(color),0),thickness=1)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,0.35,(0,255,0),1)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+70,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,0.35,(0,255,0),1)

    return img,objectInfo


def getFramesGenerator():
    """Генератор кадров для вывода на веб-страницу."""
    while True:
        success, img = camera.read()  # Получаем кадр с камеры
        if not success:
            continue  # Пропустить кадр, если не удалось получить
        img = cv2.rotate(img, cv2.ROTATE_180)

        cv2.putText(img, 'TEXT: {}'.format(isee), (8, 140),
              cv2.FONT_HERSHEY_SIMPLEX, 0.3, (50, 0, 0), 1, cv2.LINE_AA) 

        if isee == False:
            result, objectInfo = getObjects(img,0.60,0.2, objects=['person'])

        _, buffer = cv2.imencode('.jpg', img)
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
