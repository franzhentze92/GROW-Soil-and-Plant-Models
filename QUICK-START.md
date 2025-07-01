# 🚀 Quick Start Guide - GROW Soil and Plant Models

## One-Click Startup Scripts

I've created two startup scripts that will automatically set up everything you need to run the application:

### Option 1: PowerShell Script (Recommended)
```powershell
# Right-click on start-app.ps1 and select "Run with PowerShell"
# OR open PowerShell and run:
.\start-app.ps1
```

### Option 2: Batch File
```cmd
# Double-click start-app.bat
# OR open Command Prompt and run:
start-app.bat
```

## What the Scripts Do Automatically:

1. ✅ **Check Python Installation** - Verifies Python is installed
2. ✅ **Create Virtual Environment** - Sets up isolated Python environment
3. ✅ **Activate Environment** - Activates the virtual environment
4. ✅ **Upgrade pip** - Updates package installer
5. ✅ **Install Dependencies** - Installs all required packages from requirements.txt
6. ✅ **Run Database Migrations** - Sets up the database
7. ✅ **Collect Static Files** - Prepares static assets
8. ✅ **Start Django Server** - Launches the development server

## After Running the Script:

The application will be available at:
- **User Dashboard**: http://127.0.0.1:8000/api/set-cookie/?role=user
- **Agronomist Dashboard**: http://127.0.0.1:8000/api/set-cookie/?role=agronomist
- **Admin Panel**: http://127.0.0.1:8000/admin/

## To Stop the Server:
Press `Ctrl+C` in the terminal/command prompt window.

## Troubleshooting:

### If PowerShell script won't run:
1. Right-click on `start-app.ps1`
2. Select "Properties"
3. Check "Unblock" if available
4. Or run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### If you get permission errors:
- Make sure you're running as a regular user (not administrator)
- Try running the batch file instead

### If Python is not found:
- Install Python 3.9+ from https://python.org
- Make sure to check "Add Python to PATH" during installation

## Manual Setup (if scripts don't work):

If you prefer to set up manually:

```bash
# 1. Create virtual environment
python -m venv ven

# 2. Activate it (Windows)
ven\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Start server
python manage.py runserver
```

## Next Time You Want to Run the App:

Just double-click `start-app.bat` or run `.\start-app.ps1` again!
The script will skip steps that are already completed and go straight to starting the server. 