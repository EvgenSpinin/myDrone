import cv2
import subprocess

# Опции ffmpeg для кодирования в H.264 и отправки по UDP
ffmpeg_cmd = [
    "ffmpeg",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-pix_fmt", "bgr24",
    "-s", "640x480",
    "-i", "-",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-f", "rtp",
    "udp://192.168.0.110:5600"
]

# Захват видео с помощью OpenCV
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Запуск ffmpeg
ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Отправляем кадр в ffmpeg
    ffmpeg_process.stdin.write(frame.tobytes())

# Закрываем захват видео и завершаем ffmpeg
cap.release()
ffmpeg_process.stdin.close()
ffmpeg_process.wait()


