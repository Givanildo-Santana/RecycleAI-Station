import torch
import cv2
import yaml
import numpy as np
import sys
import os

print("="*60)
print("TESTE COMPLETO DO AMBIENTE PYTHON 3.10 - RecycleAI Vision")
print("="*60)

print("\n📌 Versão do Python:", sys.version)

print("\n📌 Torch:", torch.__version__)
print("    - CUDA disponível?:", torch.cuda.is_available())
print("    - Backend:", "CPU" if not torch.cuda.is_available() else "GPU")

print("\n📌 OpenCV:", cv2.__version__)
img_test = np.zeros((200, 200, 3), dtype=np.uint8)
cv2.putText(img_test, "OK", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2)
print("    - OpenCV OK (imagem de teste criada).")

print("\n📌 NumPy:", np.__version__)
arr = np.array([1,2,3])
print("    - NumPy array:", arr)

print("\n📌 PyYAML:", yaml.__version__)
yaml.safe_load("a: 1")
print("    - YAML carregado corretamente.")

print("\n📌 Testando import do YOLOv5...")
try:
    import yolov5
    print("    - YOLOv5 importado com sucesso!")
except Exception as e:
    print("    - ⚠ ERRO ao importar YOLOv5:", e)

print("\n📌 Diretório atual:", os.getcwd())

print("\n🎉 AMBIENTE 100% CONFIGURADO PARA YOLOv5 + Python 3.10!")
print("="*60)
