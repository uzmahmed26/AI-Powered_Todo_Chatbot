# ============================================================================
# Install DigitalOcean CLI (doctl) on Windows
# ============================================================================
# Run this script in PowerShell as Administrator
# Usage: .\scripts\setup\install-doctl-windows.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host "=================================" -ForegroundColor Green
Write-Host "Installing DigitalOcean CLI (doctl)" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Download URL for latest doctl Windows release
$DOCTL_VERSION = "1.115.0"
$DOWNLOAD_URL = "https://github.com/digitalocean/doctl/releases/download/v$DOCTL_VERSION/doctl-$DOCTL_VERSION-windows-amd64.zip"
$TEMP_DIR = "$env:TEMP\doctl-install"
$INSTALL_DIR = "C:\doctl"

# Create temp directory
Write-Host "[1/5] Creating temporary directory..." -ForegroundColor Blue
New-Item -ItemType Directory -Force -Path $TEMP_DIR | Out-Null

# Download doctl
Write-Host "[2/5] Downloading doctl v$DOCTL_VERSION..." -ForegroundColor Blue
$ZIP_FILE = "$TEMP_DIR\doctl.zip"
Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $ZIP_FILE

# Extract archive
Write-Host "[3/5] Extracting archive..." -ForegroundColor Blue
Expand-Archive -Path $ZIP_FILE -DestinationPath $TEMP_DIR -Force

# Install to C:\doctl
Write-Host "[4/5] Installing to $INSTALL_DIR..." -ForegroundColor Blue
if (-not (Test-Path $INSTALL_DIR)) {
    New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null
}
Copy-Item "$TEMP_DIR\doctl.exe" -Destination "$INSTALL_DIR\doctl.exe" -Force

# Add to PATH
Write-Host "[5/5] Adding to system PATH..." -ForegroundColor Blue
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($currentPath -notlike "*$INSTALL_DIR*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$INSTALL_DIR", "Machine")
    Write-Host "Added $INSTALL_DIR to system PATH" -ForegroundColor Green
} else {
    Write-Host "$INSTALL_DIR is already in PATH" -ForegroundColor Yellow
}

# Cleanup
Remove-Item -Recurse -Force $TEMP_DIR

Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "doctl installed to: $INSTALL_DIR\doctl.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Close and reopen PowerShell/Terminal for PATH changes to take effect" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Close this PowerShell window" -ForegroundColor White
Write-Host "  2. Open a new PowerShell window" -ForegroundColor White
Write-Host "  3. Verify installation: doctl version" -ForegroundColor White
Write-Host "  4. Authenticate: doctl auth init" -ForegroundColor White
Write-Host ""
