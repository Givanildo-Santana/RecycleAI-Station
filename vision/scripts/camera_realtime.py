# ====================================================
#  SCRIPT DE DETECÇÃO EM TEMPO REAL — RecicleAI Vision
#  Com ROI dinâmica + leitura do config.yaml
# ====================================================

import cv2
import os
import sys
import yaml
import torch
import numpy as np

# ========== CARREGAR CONFIG ==========

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

# ========== CAMINHOS ==========

YOLOV5_PATH = os.path.join(BASE_DIR, cfg["paths"]["yolov5"])
WEIGHTS = os.path.join(BASE_DIR, cfg["paths"]["weights_torchscript"])
DATA_YAML = os.path.join(BASE_DIR, cfg["paths"]["data_yaml"])

# 🔥 FIX — GARANTIR QUE O PYTHON ENXERGUE O YOLOv5 CORRETAMENTE
sys.path.insert(0, BASE_DIR)       # raiz /vision
sys.path.insert(0, YOLOV5_PATH)    # pasta /vision/yolov5

# ======== IMPORTS DO YOLOv5 =========
from yolov5.utils.general import non_max_suppression, scale_boxes
from yolov5.utils.augmentations import letterbox

# ========== PARÂMETROS DO CONFIG ==========

CONF_THRES = cfg["realtime"]["conf_thres"]
IOU_THRES  = cfg["realtime"]["iou_thres"]
SOURCE     = cfg["realtime"]["source"]
DEVICE     = cfg["realtime"]["device"]

IMG_SIZE   = cfg["training"]["img_size"]

ROI_X1 = cfg["realtime"]["roi_x_start"]
ROI_X2 = cfg["realtime"]["roi_x_end"]
ROI_Y1 = cfg["realtime"]["roi_y_start"]
ROI_Y2 = cfg["realtime"]["roi_y_end"]

# ========== CARREGAR CLASSES ==========

with open(DATA_YAML, "r", encoding="utf-8") as f:
    names = yaml.safe_load(f)["names"]

# ========== CARREGAR MODELO ==========

print("🔄 Carregando modelo TorchScript...")
model = torch.jit.load(WEIGHTS, map_location=DEVICE).eval()
print("✔ Modelo carregado!")


# ========== LOOP DE CÂMERA ==========

cap = cv2.VideoCapture(SOURCE)

if not cap.isOpened():
    raise RuntimeError("❌ Não foi possível abrir a câmera.")

print("🎥 Detecção iniciada (pressione Q para sair).")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Falha ao capturar frame.")
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

    if pred is not None and len(pred):
        pred[:, :4] = scale_boxes(img.shape[2:], pred[:, :4], frame.shape).round()

        for *xyxy, conf, cls_id in pred:
            x1, y1, x2, y2 = map(int, xyxy)
            label = f"{names[int(cls_id)]} {conf:.2f}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("RecicleAI - Realtime", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("🛑 Detecção encerrada.")
