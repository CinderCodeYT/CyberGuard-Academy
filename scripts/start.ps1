<#
.SYNOPSIS
    CyberGuard Academy Startup Script for Windows (PowerShell)
.DESCRIPTION
    This script helps you quickly start the application on Windows.
    It checks configuration, cleans up old processes, and starts the API and UI.
#>

$ErrorActionPreference = "Stop"

# Get the directory where the script is located and navigate to project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "🛡️  CyberGuard Academy Startup" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "📂 Working directory: $(Get-Location)"
Write-Host ""

# Create logs directory if it doesn't exist
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️ No .env file found!" -ForegroundColor Yellow
    Write-Host "📝 Creating .env from .env.example..."
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "⚠️ Please edit .env and configure your AI provider" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   For Groq (Recommended - Free):"
    Write-Host "   1. Get API key from: https://console.groq.com/"
    Write-Host "   2. Set: AI_PROVIDER=groq"
    Write-Host "   3. Set: GROQ_API_KEY=your_key_here"
    Write-Host ""
    Write-Host "   After configuration, run this script again."
    exit 1
}

# Parse .env file manually since we can't source it like bash
$EnvContent = Get-Content ".env"
$AiProvider = ""
$GroqKey = ""
$GoogleProject = ""

foreach ($line in $EnvContent) {
    if ($line -match "^AI_PROVIDER=(.*)") { $AiProvider = $matches[1].Trim('"').Trim("'") }
    if ($line -match "^GROQ_API_KEY=(.*)") { $GroqKey = $matches[1].Trim('"').Trim("'") }
    if ($line -match "^GOOGLE_CLOUD_PROJECT=(.*)") { $GoogleProject = $matches[1].Trim('"').Trim("'") }
}

if ([string]::IsNullOrWhiteSpace($AiProvider)) {
    Write-Host "⚠️ AI_PROVIDER not set in .env" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Please edit .env and set:"
    Write-Host "   AI_PROVIDER=groq  (recommended)"
    Write-Host ""
    exit 1
}

# Check API key based on provider
if ($AiProvider -eq "groq") {
    if ([string]::IsNullOrWhiteSpace($GroqKey) -or $GroqKey -notmatch "gsk_") {
        Write-Host "⚠️ GROQ_API_KEY not configured correctly in .env" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   Please edit .env and add your Groq API key:"
        Write-Host "   GROQ_API_KEY=gsk_your_key_here"
        Write-Host ""
        Write-Host "   Get your free API key from: https://console.groq.com/"
        exit 1
    }
} elseif ($AiProvider -eq "vertex") {
    if ([string]::IsNullOrWhiteSpace($GoogleProject)) {
        Write-Host "⚠️ GOOGLE_CLOUD_PROJECT not configured in .env" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   Please edit .env and add your GCP project ID"
        Write-Host "   GOOGLE_CLOUD_PROJECT=your-project-id"
        exit 1
    }
} else {
    Write-Host "⚠️ Invalid AI_PROVIDER: $AiProvider" -ForegroundColor Red
    Write-Host "   Must be 'groq' or 'vertex'"
    exit 1
}

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "🔧 Activating virtual environment..."
    & ".\.venv\Scripts\Activate.ps1"
}

# Kill existing processes on ports 8000 and 8501
Write-Host "🧹 Cleaning up any existing processes..."
$Ports = @(8000, 8501)
foreach ($Port in $Ports) {
    $Process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($Process) {
        Stop-Process -Id $Process.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 1

# Start API Server
Write-Host "🚀 Starting API Server..."
# Note: PowerShell Start-Process cannot redirect stdout and stderr to the same file directly.
# We split them into .log (stdout) and .err (stderr).
$ApiProcess = Start-Process -FilePath "uvicorn" -ArgumentList "api:app", "--host", "0.0.0.0", "--port", "8000" -RedirectStandardOutput "logs\api.log" -RedirectStandardError "logs\api.err" -PassThru -NoNewWindow

# Wait for API to be ready
Write-Host "⏳ Waiting for API to be ready (initializing agents)..."
$MaxRetries = 30
$RetryCount = 0
$ApiReady = $false

while ($RetryCount -lt $MaxRetries) {
    try {
        $Response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction Stop
        if ($Response.StatusCode -eq 200) {
            $ApiReady = $true
            Write-Host "✅ API Server is ready!" -ForegroundColor Green
            break
        }
    } catch {
        # Ignore connection errors while waiting
    }
    
    if ($RetryCount % 3 -eq 0) {
        Write-Host "   Still initializing... ($RetryCount s elapsed)"
    }
    
    Start-Sleep -Seconds 1
    $RetryCount++
}

if (-not $ApiReady) {
    Write-Host "❌ API Server failed to start within 30 seconds. Check logs\api.err for details." -ForegroundColor Red
    Write-Host ""
    Write-Host "Last 20 lines of logs\api.err:"
    if (Test-Path "logs\api.err") {
        Get-Content "logs\api.err" -Tail 20
    }
    Stop-Process -Id $ApiProcess.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""

# Start Streamlit UI
Write-Host "🎨 Starting Streamlit UI..."
$UiProcess = Start-Process -FilePath "streamlit" -ArgumentList "run", "ui.py", "--server.headless", "true" -RedirectStandardOutput "logs\ui.log" -RedirectStandardError "logs\ui.err" -PassThru -NoNewWindow

Write-Host ""
Write-Host "✅ CyberGuard Academy is running!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Access the application:"
Write-Host "   - Web UI: http://localhost:8501"
Write-Host "   - API Docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "📝 Logs:"
Write-Host "   - API: logs\api.log (stdout), logs\api.err (stderr)"
Write-Host "   - UI: logs\ui.log (stdout), logs\ui.err (stderr)"
Write-Host ""
Write-Host "Press Enter to stop all services..."

Read-Host

# Cleanup on exit
Write-Host "🛑 Shutting down CyberGuard Academy..."
Stop-Process -Id $ApiProcess.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $UiProcess.Id -Force -ErrorAction SilentlyContinue
Write-Host "✅ Shutdown complete"
