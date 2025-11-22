import os
import sys
import torch
from yolov5.utils.general import non_max_suppression, scale_boxes
from yolov5.utils.augmentations import letterbox

def setup_paths(base_dir, yolo_path):
    full_yolo_path = os.path.join(base_dir, yolo_path)
    sys.path.insert(0, base_dir)
    sys.path.insert(0, full_yolo_path)
    return full_yolo_path

def load_model(weights_path, device):
    model = torch.jit.load(weights_path, map_location=device).eval()
    return model

# Exportar funções do YOLO
__all__ = ["non_max_suppression", "scale_boxes", "letterbox"]
