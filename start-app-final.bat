@echo off
echo ========================================
echo    GROW Soil and Plant Models
echo    Startup Script (Final Working Version)
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo ✓ Python found
echo.

:: Remove old virtual environment if it has wrong structure
if exist "ven\bin" (
    echo Removing old virtual environment with incorrect structure...
    rmdir /s /q ven
    echo ✓ Old virtual environment removed
)

:: Check if virtual environment exists
if not exist "ven" (
    echo Creating virtual environment...
    python -m venv ven
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

:: Activate virtual environment
echo.
echo Activating virtual environment...
call ven\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Trying to recreate virtual environment...
    rmdir /s /q ven
    python -m venv ven
    call ven\Scripts\activate.bat
    if errorlevel 1 (
        echo ERROR: Still failed to activate virtual environment
        pause
        exit /b 1
    )
)
echo ✓ Virtual environment activated

:: Upgrade pip and setuptools
echo.
echo Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel
echo ✓ Pip and setuptools upgraded

:: Install dependencies using working requirements
echo.
echo Installing dependencies (using working versions)...
if exist "requirements-working.txt" (
    pip install --only-binary=all -r requirements-working.txt
) else (
    echo WARNING: requirements-working.txt not found, trying original requirements...
    pip install --only-binary=all -r requirements.txt
)

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

:: Install psycopg2-binary for PostgreSQL support (required for migrations)
echo.
echo Installing psycopg2-binary (PostgreSQL driver)...
pip install psycopg2-binary
if errorlevel 1 (
    echo ERROR: Failed to install psycopg2-binary
    pause
    exit /b 1
)
echo ✓ psycopg2-binary installed

:: Set environment variables in the virtual environment
echo.
echo Setting up environment variables...
set OPENAI_API_KEY=dummy_key_for_development
set AWS_ACCESS_KEY_ID=dummy_aws_key
set AWS_SECRET_ACCESS_KEY=dummy_aws_secret
set AWS_REGION=us-east-1
set S3_RESPONSE_BUCKET=dummy_bucket
set S3_CSV_BUCKET=dummy_bucket
echo ✓ Environment variables set

:: Run migrations (use correct manage.py path if needed)
echo.
echo Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)
echo ✓ Database migrations completed

:: Collect static files
echo.
echo Collecting static files...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo WARNING: Failed to collect static files (this is usually okay)
) else (
    echo ✓ Static files collected
)

echo.
echo ========================================
echo    Starting Django Development Server
echo ========================================
echo.
echo The application will be available at:
echo   - User Dashboard: http://127.0.0.1:8000/api/set-cookie/?role=user
echo   - Agronomist Dashboard: http://127.0.0.1:8000/api/set-cookie/?role=agronomist
echo   - Admin Panel: http://127.0.0.1:8000/admin/
echo.
echo Press Ctrl+C to stop the server
echo.

:: Start the Django server with environment variables
python manage.py runserver 