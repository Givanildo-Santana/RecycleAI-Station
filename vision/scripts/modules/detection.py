import torch
import numpy as np
from .model_loader import non_max_suppression, scale_boxes, letterbox

def run_inference(model, frame, device, img_size, conf_thres, iou_thres, names):
    img = letterbox(frame, img_size, stride=32, auto=True)[0]
    img = img.transpose((2, 0, 1))
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(device).float() / 255.0
    img = img.unsqueeze(0)

    with torch.no_grad():
        pred = model(img)[0]

    pred = non_max_suppression(pred, conf_thres, iou_thres)[0]

    detected_label = "NONE"
    detections = []

    if pred is not None and len(pred):
        pred[:, :4] = scale_boxes(img.shape[2:], pred[:, :4], frame.shape).round()

        for *xyxy, conf, cls_id in pred:
            x1, y1, x2, y2 = map(int, xyxy)
            label = names[int(cls_id)].upper()
            detected_label = label
            detections.append((x1, y1, x2, y2, label, conf))

    return detected_label, detections

