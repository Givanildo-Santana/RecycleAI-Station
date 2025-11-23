# ===============================================
#  Instalador automático para Windows
#  - Instala Python 3.10 se faltar
#  - Adiciona ao PATH
#  - Executa install.py
# ===============================================

Write-Host "🔍 Verificando instalação do Python 3.10..."

$python310 = Get-Command python3.10 -ErrorAction SilentlyContinue
$python = Get-Command python -ErrorAction SilentlyContinue

$pythonOK = $false

# ===== PASSO 1 — Verificar se já existe Python 3.10 =====
if ($python310) {
    Write-Host "✔ Python 3.10 encontrado em $($python310.Source)"
    $pythonOK = $true
} elseif ($python) {
    # Testa se python existente é 3.10
    $ver = python -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')" 2>$null
    if ($ver -eq "3.10") {
        Write-Host "✔ Python 3.10 encontrado (python)"
        $pythonOK = $true
    }
}

# ===== PASSO 2 — Instalar Python se NÃO existir =====
if (-not $pythonOK) {
    Write-Host "⚠ Python 3.10 não encontrado. Baixando instalador..."

    $url = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    $installer = "$env:TEMP\python310_installer.exe"

    Invoke-WebRequest $url -OutFile $installer

    Write-Host "📦 Instalando Python 3.10 silenciosamente..."
    Start-Process $installer -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait

    Write-Host "✔ Python 3.10 instalado."
}

# ===== PASSO 3 — Rodar o install.py =====
Write-Host "🚀 Executando install.py..."
python install.py
