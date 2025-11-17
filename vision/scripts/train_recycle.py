# =============================================================
#  SCRIPT DE TREINAMENTO YOLOv5 (RECYCLEAI-VISION)
#  Totalmente configurado via config.yaml
#  Sem caminhos absolutos — 100% compatível com GitHub
# =============================================================

import subprocess      # ← executar o train.py
import os              # ← manipulação de caminhos
import sys             # ← acesso ao Python do venv
import yaml            # ← leitura do config.yaml

# =============================================================
#  1) CARREGAR BASE_DIR E CONFIG
# =============================================================

# BASE_DIR = pasta raiz do projeto vision/
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")  # scripts → vision
)

# Caminho até config.yaml
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

# Carrega configuração
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

# Pasta do YOLOv5 dentro de vision/
YOLOV5_DIR = os.path.join(BASE_DIR, cfg["paths"]["yolov5"])

# =============================================================
#  2) DEFINIR CAMINHO DO DATASET (RELATIVO AO YOLOv5)
# =============================================================
# IMPORTANTE:
# O script train.py é executado *dentro da pasta YOLOv5*
# Portanto o caminho deve ser relativo a ela.

DATA_YAML = os.path.normpath(
    os.path.join("..", cfg["paths"]["data_yaml"])
)

# Caminho REAL (apenas validação)
VALIDATE_DATA_PATH = os.path.join(YOLOV5_DIR, DATA_YAML)

# =============================================================
#  3) VERIFICAÇÕES
# =============================================================

print("\n🔍 Verificando ambiente...\n")

if not os.path.exists(YOLOV5_DIR):
    raise FileNotFoundError(f"❌ YOLOv5 não encontrado em: {YOLOV5_DIR}")

if not os.path.exists(VALIDATE_DATA_PATH):
    raise FileNotFoundError(
        f"❌ O YOLOv5 NÃO consegue acessar o data.yaml!\n"
        f"   Caminho que ele irá usar: {VALIDATE_DATA_PATH}\n"
        f"   Verifique se está assim:\n"
        f"   vision/datasets/dataset_manual/data.yaml"
    )

print("✔ YOLOv5 encontrado")
print("✔ data.yaml encontrado")

# =============================================================
#  4) HIPERPARÂMETROS DO TREINO
# =============================================================

img_size = cfg["training"]["img_size"]
batch = cfg["training"]["batch"]
epochs = cfg["training"]["epochs"]
weights = cfg["training"]["pretrained_weights"]
run_name = cfg["training"]["run_name"]
models_dir = cfg["paths"]["models"]
device = cfg["realtime"]["device"]

# =============================================================
#  5) MONTAGEM DO COMANDO FINAL DE TREINO
# =============================================================

PYTHON = sys.executable  # Python do venv

CMD = [
    PYTHON,
    os.path.join(YOLOV5_DIR, "train.py"),

    "--img", str(img_size),
    "--batch", str(batch),
    "--epochs", str(epochs),

    # Agora correto: caminho RELATIVO ao YOLOv5
    "--data", DATA_YAML,

    "--weights", weights,
    "--project", models_dir,
    "--name", run_name,
    "--workers", "8",
    "--device", device,
    "--exist-ok",
    "--cache",
    "--cos-lr",
    "--label-smoothing", "0.1"
]

print("\n🚀 Comando executado:")
print(" ".join(CMD), "\n")

# =============================================================
#  6) EXECUTAR TREINAMENTO COM LOG AO VIVO
# =============================================================

process = subprocess.Popen(
    CMD,
    cwd=YOLOV5_DIR,            # ← EXECUTA DENTRO DO PASTA YOLOv5 (ESSENCIAL)
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
    errors="ignore"            # ← Evita UnicodeDecodeError no Windows
)

for line in process.stdout:
    print(line, end="")

process.wait()

print("\n🎉 Treinamento finalizado!\n")
