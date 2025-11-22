#!/usr/bin/env python
"""
Instalador automático do ambiente RecicleAI-Station.

- Detecta SO (Windows / Linux / macOS)
- Procura Python 3.10 (usa se encontrar)
- Cria venv em vision/venv
- Instala requirements_windows.txt ou requirements_linux.txt
- Detecta GPU NVIDIA (nvidia-smi)
- Instala Torch GPU (CUDA 12.1) ou Torch CPU
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
VISION_DIR = PROJECT_ROOT / "vision"
VENV_DIR = VISION_DIR / "venv"


def log(msg: str):
    print(msg)


def run(cmd, env=None, cwd=None) -> int:
    """Roda um comando e retorna o código de saída."""
    log(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env, cwd=cwd)
    return result.returncode


def detect_os() -> str:
    system = platform.system().lower()
    if system.startswith("win"):
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return system


def find_python_310() -> str | None:
    """
    Tenta encontrar um executável Python 3.10 no sistema.
    Retorna o caminho se encontrar, ou None se não achar.
    """
    candidates = []

    system = detect_os()
    if system == "windows":
        # tenta 'py -3.10' e python3.10
        candidates = ["python3.10", "python", "py"]
    else:
        candidates = ["python3.10", "python3", "python"]

    for exe in candidates:
        path = shutil.which(exe)
        if not path:
            continue
        try:
            out = subprocess.check_output(
                [path, "-c", "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"],
                text=True
            ).strip()
            if out == "3.10":
                return path
        except Exception:
            continue

    return None


def choose_python_executable() -> str:
    """
    Decide qual Python usar para criar o venv:
    - se achar Python 3.10, usa ele
    - senão, usa o próprio sys.executable e avisa
    """
    log("🔍 Verificando Python 3.10 disponível no sistema...")
    py310 = find_python_310()
    if py310:
        log(f"✔ Python 3.10 encontrado em: {py310}")
        return py310

    # Se chegou aqui, não achou 3.10
    current = sys.executable
    v = sys.version_info
    log(f"⚠ Python 3.10 NÃO encontrado. Usando o Python atual: {current} (versão {v.major}.{v.minor})")
    log("⚠ Se você quiser garantir 3.10, instale manualmente e rode o instalador com ele.")
    return current


def create_venv(python_exe: str):
    if VENV_DIR.exists():
        log(f"⚠ venv já existe em: {VENV_DIR}")
        return

    log(f"📦 Criando venv em: {VENV_DIR}")
    rc = run([python_exe, "-m", "venv", str(VENV_DIR)])
    if rc != 0:
        log("❌ Erro ao criar o venv.")
        sys.exit(1)
    log("✔ venv criado com sucesso.")


def get_venv_python_and_pip():
    system = detect_os()
    if system == "windows":
        python_path = VENV_DIR / "Scripts" / "python.exe"
        pip_path = VENV_DIR / "Scripts" / "pip.exe"
    else:
        python_path = VENV_DIR / "bin" / "python"
        pip_path = VENV_DIR / "bin" / "pip"

    if not python_path.exists():
        log(f"❌ Python do venv não encontrado em: {python_path}")
        sys.exit(1)

    return str(python_path), str(pip_path)


def upgrade_pip_tools(pip_exe: str):
    log("🔧 Atualizando pip, setuptools e wheel dentro do venv...")
    rc = run([pip_exe, "install", "--upgrade", "pip", "setuptools", "wheel"])
    if rc != 0:
        log("⚠ Não foi possível atualizar pip/setuptools/wheel. Continuando assim mesmo...")


def install_requirements(pip_exe: str, os_name: str):
    if os_name == "windows":
        req_file = PROJECT_ROOT / "requirements_windows.txt"
    else:
        # linux e macos usam o mesmo base (nomeado linux)
        req_file = PROJECT_ROOT / "requirements_linux.txt"

    if not req_file.exists():
        log(f"⚠ Arquivo de requirements não encontrado: {req_file}")
        log("   Pule esta etapa ou crie o arquivo antes de rodar o instalador.")
        return

    log(f"📦 Instalando dependências base de: {req_file.name}")
    rc = run([pip_exe, "install", "-r", str(req_file)])
    if rc != 0:
        log("❌ Erro ao instalar dependências base.")
        sys.exit(1)
    log("✔ Dependências base instaladas.")


def has_nvidia_gpu() -> bool:
    try:
        rc = run(["nvidia-smi"])
        return rc == 0
    except FileNotFoundError:
        return False


def install_torch(pip_exe: str, os_name: str):
    log("🔍 Detectando GPU para instalar Torch...")

    gpu_available = has_nvidia_gpu()

    # versões fixas (iguais às que você já usa)
    torch_ver = "2.5.1"
    tv_ver = "0.20.1"
    ta_ver = "2.5.1"

    if os_name in ("linux", "windows") and gpu_available:
        log("✔ GPU NVIDIA detectada. Instalando Torch com CUDA 12.1...")
        index_url = "https://download.pytorch.org/whl/cu121"
    else:
        log("⚠ GPU NVIDIA não detectada ou SO sem suporte CUDA. Instalando Torch CPU...")
        index_url = "https://download.pytorch.org/whl/cpu"

    cmd = [
        pip_exe,
        "install",
        f"torch=={torch_ver}",
        f"torchvision=={tv_ver}",
        f"torchaudio=={ta_ver}",
        "--index-url",
        index_url,
    ]
    rc = run(cmd)
    if rc != 0:
        log("❌ Erro ao instalar Torch. Verifique mensagens acima.")
        sys.exit(1)

    log("✔ Torch instalado com sucesso.")


def main():
    log("===========================================")
    log("   RecicleAI-Station – Instalador Automático")
    log("===========================================\n")

    os_name = detect_os()
    log(f"🖥  Sistema operacional detectado: {os_name}")

    if not VISION_DIR.exists():
        log(f"❌ Pasta 'vision' não encontrada em: {VISION_DIR}")
        log("   Certifique-se de rodar este script na raiz de 'RecycleAI-Station'.")
        sys.exit(1)

    # 1) Escolher Python
    python_exe = choose_python_executable()

    # 2) Criar venv
    create_venv(python_exe)

    # 3) Localizar python/pip do venv
    venv_python, venv_pip = get_venv_python_and_pip()
    log(f"🐍 Python do venv: {venv_python}")
    log(f"📦 Pip do venv:    {venv_pip}")

    # 4) Atualizar pip/setuptools/wheel
    upgrade_pip_tools(venv_pip)

    # 5) Instalar requisitos base
    install_requirements(venv_pip, os_name)

    # 6) Instalar Torch adequado
    install_torch(venv_pip, os_name)

    log("\n✅ Instalação concluída com sucesso!")
    log("Agora você pode ativar o venv e rodar seu projeto:\n")

    if os_name == "windows":
        log(r"    cd vision")
        log(r"    venv\Scripts\activate")
        log(r"    python scripts\main.py")
    else:
        log("    cd vision")
        log("    source venv/bin/activate")
        log("    python scripts/main.py")

    log("\n🚀 RecicleAI pronto para uso!")


if __name__ == "__main__":
    main()
