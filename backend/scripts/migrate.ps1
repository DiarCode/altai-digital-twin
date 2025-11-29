# PowerShell script to apply prisma migrations and generate client
cd $PSScriptRoot\\..\
if (Test-Path .\.venv\Scripts\Activate.ps1) {
    Write-Host "Activating venv..."
    . .\.venv\Scripts\Activate.ps1
}

pip install -r requirements.txt

# Requires prisma CLI available; instructions: pip install prisma
prisma generate
prisma migrate deploy

Write-Host "Migrations applied."
