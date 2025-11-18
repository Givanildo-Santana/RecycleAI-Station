<#
==========================================================
   INSTALL RECYCLEAI - INSTALADOR OFICIAL
   Compatível com QUALQUER Windows
   Venv + Pip + Requirements + Download do Modelo
==========================================================
#>

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         🚀 INSTALADOR DO PROJETO RECYCLEAI                " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# --------------------------------------------------------------------
# 1. Local do script (garante que tudo funcione em qualquer lugar)
# --------------------------------------------------------------------
$BasePath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "📂 Pasta do instalador:" $BasePath

# --------------------------------------------------------------------
# 2. Habilitar execução de scripts (caso bloqueado)
# --------------------------------------------------------------------
try {
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
    Write-Host "✔ Permissão de execução garantida." -ForegroundColor Green
}
catch {
    Write-Host "⚠ Aviso: Não foi possível definir ExecutionPolicy. Tentando continuar..." -ForegroundColor Yellow
}

# --------------------------------------------------------------------
# 3. Verificar instalação do Python
# --------------------------------------------------------------------
Write-Host "`n🔍 Verificando Python..."

$python = Get-Command python -ErrorAction SilentlyContinue

if (-not $python) {
    Write-Host "❌ Python NÃO encontrado! Instale o Python 3.10 antes de continuar." -ForegroundColor Red
    pause
    exit
}

Write-Host "✔ Python encontrado:" $python.Source -ForegroundColor Green

# --------------------------------------------------------------------
# 4. Criar / ativar ambiente virtual
# --------------------------------------------------------------------
Write-Host "`n🔧 Configurando ambiente virtual..."

$VenvPath = Join-Path $BasePath "venv"
$ActivateScript = Join-Path $VenvPath "Scripts\activate.ps1"

if (-Not (Test-Path $VenvPath)) {
    Write-Host "📦 Criando venv..."
    python -m venv $VenvPath
} else {
    Write-Host "✔ venv já existe."
}

Write-Host "⚡ Ativando venv..."
& $ActivateScript
Write-Host "✔ venv ativado." -ForegroundColor Green

# --------------------------------------------------------------------
# 5. Atualizar pip dentro do venv
# --------------------------------------------------------------------
Write-Host "`n⬆ Atualizando pip..."
& "$VenvPath\Scripts\python.exe" -m pip install --upgrade pip

# --------------------------------------------------------------------
# 6. Instalar dependências (sempre no mesmo diretório do instalador)
# --------------------------------------------------------------------
$ReqFile = Join-Path $BasePath "requirements.txt"

if (-not (Test-Path $ReqFile)) {
    Write-Host "❌ ARQUIVO requirements.txt NÃO encontrado!" -ForegroundColor Red
    Write-Host "Caminho esperado: $ReqFile"
    pause
    exit
}

Write-Host "`n📦 Instalando dependências a partir de requirements.txt..."
& "$VenvPath\Scripts\python.exe" -m pip install -r $ReqFile

Write-Host "✔ Dependências instaladas." -ForegroundColor Green

# --------------------------------------------------------------------
# 7. Baixar modelo treinado (se não existir)
# --------------------------------------------------------------------
Write-Host "`n🔍 Verificando modelo treinado..."

$ModelDir = Join-Path $BasePath "models\torchscript"
$ModelFile = Join-Path $ModelDir "best_ts.pt"
$DownloadURL = "https://github.com/Givanildo-Santana/RecycleAI-Station/releases/download/v1.0/best_ts.pt"

if (!(Test-Path $ModelFile)) {

    Write-Host "⬇ Modelo não encontrado. Baixando automaticamente..."
    
    if (!(Test-Path $ModelDir)) {
        New-Item -ItemType Directory -Path $ModelDir | Out-Null
    }

    Invoke-WebRequest -Uri $DownloadURL -OutFile $ModelFile

    Write-Host "✔ Modelo baixado com sucesso!" -ForegroundColor Green
}
else {
    Write-Host "✔ Modelo já existe." -ForegroundColor Green
}

# --------------------------------------------------------------------
# 8. Instalação concluída
# --------------------------------------------------------------------
Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "     🎉 INSTALAÇÃO FINALIZADA COM SUCESSO!                " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "`nAgora você já pode executar:"
Write-Host "👉 python .\scripts\camera_realtime.py" -ForegroundColor Yellow
Write-Host "`nPressione ENTER para sair."
pause
