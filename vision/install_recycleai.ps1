Write-Host "============================================="
Write-Host "       INSTALADOR AUTOMÁTICO RECYCLEAI"
Write-Host "============================================="

# -------------------------------
# 1. Verificar se Python 3.10 existe
# -------------------------------
Write-Host "`nVerificando Python..."

$pythonVersion = ""
try {
    $pythonVersion = python --version 2>$null
} catch {}

if ($pythonVersion -notmatch "3\.10") {
    Write-Host "❌ Python 3.10 NÃO encontrado!"
    Write-Host "Baixando Python 3.10.11..."

    Invoke-WebRequest `
        -Uri "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe" `
        -OutFile "python_installer.exe"

    Write-Host "Instalando Python..."
    Start-Process "python_installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    Write-Host "✔ Python instalado!"
} else {
    Write-Host "✔ Python 3.10 detectado."
}

# -------------------------------
# 2. Criar venv se não existir
# -------------------------------
Write-Host "`nVerificando ambiente virtual..."

if (Test-Path "venv") {
    Write-Host "✔ venv já existe."
} else {
    Write-Host "Criando venv..."
    python -m venv venv
    Write-Host "✔ venv criado!"
}

# -------------------------------
# 3. Ativar venv
# -------------------------------
Write-Host "`nAtivando venv..."
& "venv\Scripts\activate.ps1"
Write-Host "✔ venv ativado."
python --version

# -------------------------------
# 4. Instalar dependências
# -------------------------------
Write-Host "`nInstalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "============================================="
Write-Host "✔ INSTALAÇÃO FINALIZADA COM SUCESSO!"
Write-Host "============================================="
z