# GROW Soil and Plant Models - Startup Script
# PowerShell Version

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   GROW Soil and Plant Models" -ForegroundColor Cyan
Write-Host "   Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "ven")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    try {
        python -m venv ven
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
try {
    & "ven\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run migrations
Write-Host ""
Write-Host "Running database migrations..." -ForegroundColor Yellow
try {
    python manage.py migrate
    Write-Host "✓ Database migrations completed" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to run migrations" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Collect static files
Write-Host ""
Write-Host "Collecting static files..." -ForegroundColor Yellow
try {
    python manage.py collectstatic --noinput
    Write-Host "✓ Static files collected" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Failed to collect static files (this is usually okay)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Starting Django Development Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The application will be available at:" -ForegroundColor White
Write-Host "  - User Dashboard: http://127.0.0.1:8000/api/set-cookie/?role=user" -ForegroundColor Green
Write-Host "  - Agronomist Dashboard: http://127.0.0.1:8000/api/set-cookie/?role=agronomist" -ForegroundColor Green
Write-Host "  - Admin Panel: http://127.0.0.1:8000/admin/" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the Django server
python manage.py runserver 