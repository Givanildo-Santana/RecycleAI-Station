import cv2

def open_camera(source):
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError("❌ Não foi possível abrir a câmera.")
    return cap
