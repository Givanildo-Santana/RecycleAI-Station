#!/usr/bin/env bash
set -e

echo "🔍 Verificando instalação do Python 3.10..."

PY310=$(command -v python3.10 || true)

if [ -z "$PY310" ]; then
    echo "⚠ Python 3.10 não encontrado."

    if [[ "$OSTYPE" == linux* ]]; then
        echo "📦 Instalando Python 3.10 via apt..."
        sudo apt update
        sudo apt install -y python3.10 python3.10-venv python3.10-distutils
        PY310=$(command -v python3.10)
    elif [[ "$OSTYPE" == darwin* ]]; then
        echo "📦 Instalando Python 3.10 via Homebrew..."
        brew install python@3.10
        PY310=$(brew --prefix python@3.10)/bin/python3.10
    else
        echo "❌ Sistema não reconhecido."
        exit 1
    fi
else
    echo "✔ Python 3.10 encontrado em: $PY310"
fi

echo "🚀 Executando install.py..."
$PY310 install.py
