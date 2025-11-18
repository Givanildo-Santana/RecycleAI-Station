# ====================================================
#  RecicleAI Vision – Deteção em tempo real + Serial Monitor
# ====================================================

import cv2
import os
import sys
import yaml
import torch
import numpy as np
import serial
import threading
import time

# ============================================================
#  CARREGAR CONFIG
# ============================================================

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

YOLOV5_PATH = os.path.join(BASE_DIR, cfg["paths"]["yolov5"])
WEIGHTS = os.path.join(BASE_DIR, cfg["paths"]["weights_torchscript"])
DATA_YAML = os.path.join(BASE_DIR, cfg["paths"]["data_yaml"])

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, YOLOV5_PATH)

from yolov5.utils.general import non_max_suppression, scale_boxes
from yolov5.utils.augmentations import letterbox

# ============================================================
#  PARÂMETROS DO PROJETO
# ============================================================

CONF_THRES = cfg["realtime"]["conf_thres"]
IOU_THRES = cfg["realtime"]["iou_thres"]
SOURCE = cfg["realtime"]["source"]
DEVICE = cfg["realtime"]["device"]
IMG_SIZE = cfg["training"]["img_size"]

ROI_X1 = cfg["realtime"]["roi_x_start"]
ROI_X2 = cfg["realtime"]["roi_x_end"]
ROI_Y1 = cfg["realtime"]["roi_y_start"]
ROI_Y2 = cfg["realtime"]["roi_y_end"]

SERIAL_PORT = cfg["arduino"]["port"]
BAUD_RATE = cfg["arduino"]["baudrate"]

# ============================================================
#  CARREGAR CLASSES
# ============================================================

with open(DATA_YAML, "r", encoding="utf-8") as f:
    names = yaml.safe_load(f)["names"]

# ============================================================
#  SERIAL MONITOR – THREAD PARA LER ARDUINO
# ============================================================

arduino = None
serial_running = True

def serial_monitor():
    """Thread paralela para ler mensagens do Arduino continuamente."""
    global arduino, serial_running
    while serial_running:
        if arduino is not None and arduino.in_waiting:
            try:
                msg = arduino.readline().decode(errors="ignore").strip()
                if msg:
                    print("\n─────────────────────────────────────────")
                    print(f"[ARDUINO] {msg}")
                    print("─────────────────────────────────────────\n")
            except:
                pass
        time.sleep(0.05)

# ============================================================
#  INICIAR SERIAL
# ============================================================

try:
    print(f"Tentando abrir porta {SERIAL_PORT} com baudrate {BAUD_RATE}...")
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"🔌 Arduino conectado!")
except Exception as e:
    print("⚠ ERRO AO CONECTAR NO ARDUINO:", e)
    arduino = None

# Iniciar thread do monitor
serial_thread = threading.Thread(target=serial_monitor, daemon=True)
serial_thread.start()

# ============================================================
#  CARREGAR MODELO
# ============================================================

print("🔄 Carregando modelo TorchScript...")
model = torch.jit.load(WEIGHTS, map_location=DEVICE).eval()
print("✔ Modelo carregado!")

# ============================================================
#  VARIÁVEIS DO TEMPORIZADOR
# ============================================================

classe_atual = None
tempo_inicio = None
classe_confirmada = None

# ============================================================
#  LOOP DE DETECÇÃO
# ============================================================

cap = cv2.VideoCapture(SOURCE)
if not cap.isOpened():
    raise RuntimeError("❌ Não foi possível abrir a câmera.")

print("🎥 Detecção iniciada...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.rectangle(frame, (ROI_X1, ROI_Y1), (ROI_X2, ROI_Y2), (0, 255, 255), 2)

    img = letterbox(frame, IMG_SIZE, stride=32, auto=True)[0]
    img = img.transpose((2, 0, 1))
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(DEVICE).float() / 255.0
    img = img.unsqueeze(0)

    with torch.no_grad():
        pred = model(img)[0]

    pred = non_max_suppression(pred, CONF_THRES, IOU_THRES)[0]

    detected_label = "NONE"

    if pred is not None and len(pred):

        pred[:, :4] = scale_boxes(img.shape[2:], pred[:, :4], frame.shape).round()

        for *xyxy, conf, cls_id in pred:
            label = names[int(cls_id)].upper()
            detected_label = label

            x1, y1, x2, y2 = map(int, xyxy)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}",
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0), 2)

    # ============================================================
    #  LÓGICA DOS 3 SEGUNDOS
    # ============================================================

    if detected_label != classe_atual:
        classe_atual = detected_label
        tempo_inicio = time.time()
        classe_confirmada = None

    elif time.time() - tempo_inicio >= 3 and classe_confirmada is None:
        classe_confirmada = classe_atual

        print("\n===================================================")
        print(f"✔ Classe confirmada após 3 segundos: {classe_confirmada}")
        print("===================================================\n")

        if arduino is not None:
            msg = classe_confirmada + "\n"
            arduino.write(msg.encode())
            print(f"[PYTHON] → Enviado para Arduino: {classe_confirmada}")

    cv2.imshow("RecicleAI - Realtime", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

serial_running = False
cap.release()
cv2.destroyAllWindows()
print("🛑 Detecção encerrada.")
