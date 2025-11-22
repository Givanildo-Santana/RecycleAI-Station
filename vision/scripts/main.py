import os
import cv2
import sys
import yaml

# ============================================================
#  AJUSTAR CAMINHOS DO PROJETO E ADICIONAR YOLOv5 AO PYTHONPATH
# ============================================================

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
YOLOV5_DIR = os.path.join(BASE_DIR, "yolov5")

# garantir que o Python ache os módulos
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, YOLOV5_DIR)

# ============================================================
#  IMPORTAR MÓDULOS INTERNOS
# ============================================================

from modules.config_loader import load_config
from modules.model_loader import setup_paths, load_model
from modules.serial_handler import SerialHandler
from modules.detection import run_inference
from modules.roi_timer import RoiTimer
from modules.drawing import draw_detections, draw_roi
from modules.video_source import open_camera

# ============================================================
#  CARREGAR CONFIGURAÇÕES
# ============================================================

cfg = load_config(BASE_DIR)

YOLOV5_PATH = setup_paths(BASE_DIR, cfg["paths"]["yolov5"])
MODEL_PATH = os.path.join(BASE_DIR, cfg["paths"]["weights_torchscript"])
DATA_YAML = os.path.join(BASE_DIR, cfg["paths"]["data_yaml"])

# ============================================================
#  CARREGAR CLASSES DO DATA.YAML (CORRETO)
# ============================================================

with open(DATA_YAML, "r", encoding="utf-8") as f:
    data_cfg = yaml.safe_load(f)

names = data_cfg["names"]

# ============================================================
#  CARREGAR MODELO TORCHSCRIPT
# ============================================================

print("🔄 Carregando modelo TorchScript...")
model = load_model(MODEL_PATH, cfg["realtime"]["device"])
print("✔ Modelo carregado com sucesso!")

# ============================================================
#  ARDUINO – INICIAR SERIAL
# ============================================================

serial_handler = SerialHandler(cfg["arduino"]["port"], cfg["arduino"]["baudrate"])
serial_handler.start()

# ============================================================
#  INICIAR CAPTURA DE VÍDEO
# ============================================================

cap = open_camera(cfg["realtime"]["source"])
print("🎥 Detecção iniciada...")

# Criar temporizador para lógica dos 3 segundos
timer = RoiTimer()

# ============================================================
#  LOOP PRINCIPAL DE DETECÇÃO EM TEMPO REAL
# ============================================================

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # desenhar ROI
    draw_roi(
        frame,
        cfg["realtime"]["roi_x_start"],
        cfg["realtime"]["roi_y_start"],
        cfg["realtime"]["roi_x_end"],
        cfg["realtime"]["roi_y_end"]
    )

    # rodar inferência
    detected_label, detections = run_inference(
        model=model,
        frame=frame,
        device=cfg["realtime"]["device"],
        img_size=cfg["training"]["img_size"],
        conf_thres=cfg["realtime"]["conf_thres"],
        iou_thres=cfg["realtime"]["iou_thres"],
        names=names
    )

    # desenhar detecções no frame
    draw_detections(frame, detections)

    # lógica dos 3 segundos
    confirmed = timer.update(detected_label)
    if confirmed:
        print("\n===================================================")
        print(f"✔ Classe confirmada após 3 segundos: {confirmed}")
        print("===================================================\n")
        serial_handler.send(confirmed)

    # exibir janela
    cv2.imshow("RecicleAI - Realtime", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ============================================================
#  ENCERRAR SISTEMA
# ============================================================

serial_handler.stop()
cap.release()
cv2.destroyAllWindows()

print("🛑 Detecção encerrada.")
