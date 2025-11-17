# ============================================
#  EXPORTAÇÃO YOLOv5 → TORCHSCRIPT (ROBUSTA)
# ============================================

import os
import sys
import yaml
import torch


# ============================================================
#  CONFIGURAÇÃO DOS PATHS
# ============================================================

# BASE_DIR: raiz do projeto (pasta /vision)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# YOLOv5 local
YOLOV5_PATH = os.path.join(BASE_DIR, "yolov5")

if not os.path.isdir(YOLOV5_PATH):
    raise RuntimeError(f"❌ ERRO: Pasta YOLOv5 não encontrada em:\n{YOLOV5_PATH}")

# Adiciona raiz do projeto ao PYTHONPATH
sys.path.insert(0, BASE_DIR)

print("📂 PYTHONPATH adicionou:", BASE_DIR)
print("📂 YOLOv5 encontrado em:", YOLOV5_PATH)


# ============================================================
#  CARREGANDO CONFIGURAÇÕES
# ============================================================

CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

# Caminhos do config.yaml
WEIGHTS_PT = os.path.join(BASE_DIR, cfg["paths"]["weights_pt"])

MODELS_DIR = os.path.join(BASE_DIR, cfg["paths"]["models"])
OUTPUT_DIR = os.path.join(MODELS_DIR, "torchscript")

# Arquivos de saída
OUTPUT_TS = os.path.join(OUTPUT_DIR, "best_ts.pt")
OUTPUT_ONNX = os.path.join(OUTPUT_DIR, "best.onnx")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🚀 Iniciando exportação YOLOv5 → TorchScript")


# ============================================================
#  IMPORTANDO CLASSES DO YOLOv5
# ============================================================

from yolov5.models.yolo import DetectionModel, Model as DetectModelClass
from yolov5.models.common import Conv, C3, SPPF

print("🔐 Classes YOLOv5 importadas (safe_globals ignorado).")


# ============================================================
#  FUNÇÃO PRINCIPAL DE EXPORTAÇÃO
# ============================================================

def main():

    # ---------------------------------------
    # VERIFICA SE O .PT EXISTE
    # ---------------------------------------
    if not os.path.isfile(WEIGHTS_PT):
        raise FileNotFoundError(f"❌ Pesos não encontrados em:\n{WEIGHTS_PT}")

    print(f"📦 Carregando checkpoint:\n{WEIGHTS_PT}")

    # Carrega checkpoint completo
    ckpt = torch.load(WEIGHTS_PT, map_location="cpu", weights_only=False)

    if "model" not in ckpt:
        raise RuntimeError("❌ ERRO: checkpoint NÃO contém chave 'model'!")

    # Modelo pronto
    model = ckpt["model"].float().eval()

    # Tenta extrair img_size do modelo
    imgsz = 640
    try:
        if hasattr(model, "yaml") and "img_size" in model.yaml:
            imgsz = model.yaml["img_size"]
    except:
        pass

    print(f"📐 Resolução usada para dummy input: {imgsz}x{imgsz}")

    # Dummy input
    dummy = torch.randn(1, 3, imgsz, imgsz)


    # ========================================================
    #  EXPORTAÇÃO PARA TORCHSCRIPT
    # ========================================================

    print("⚙️ Exportando para TorchScript...")

    try:
        traced = torch.jit.trace(model, dummy, check_trace=False)
        traced.save(OUTPUT_TS)

        print("\n✅ SUCESSO! Arquivo TorchScript salvo em:")
        print(OUTPUT_TS)
        return

    except Exception as e:
        print("\n❌ ERRO no TorchScript:")
        print(str(e))
        print("⚠️ Tentando fallback ONNX...")


    # ========================================================
    #  EXPORTAÇÃO PARA ONNX (FALLBACK)
    # ========================================================

    try:
        torch.onnx.export(
            model,
            dummy,
            OUTPUT_ONNX,
            opset_version=12,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={
                "input": {0: "batch", 2: "height", 3: "width"},
                "output": {0: "batch"},
            },
        )

        print("\n⚠️ TorchScript falhou, mas ONNX foi exportado:")
        print(OUTPUT_ONNX)

    except Exception as e:
        print("\n❌ ERRO também no ONNX:")
        print(str(e))
        print("💀 Falha total na exportação.")


# ============================================================
#  EXECUÇÃO DIRETA
# ============================================================

if __name__ == "__main__":
    main()
