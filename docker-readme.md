# 🌱 Crop Nutrition Dashboard - Setup Guide

This guide will help you set up and run the Crop Nutrition Dashboard on your local computer.

## 📋 Prerequisites

Before you start, you need to install Docker on your computer.

### Step 1: Install Docker Desktop

1. **Download Docker Desktop:**
   - For Windows: Go to https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
   - For Mac: Go to https://desktop.docker.com/mac/main/amd64/Docker.dmg
   - For Linux: Follow instructions at https://docs.docker.com/desktop/install/linux-install/

2. **Install Docker Desktop:**
   - Run the downloaded installer
   - Follow the installation wizard
   - Restart your computer when prompted

3. **Verify Docker is installed:**
   - Open Terminal (Mac/Linux) or Command Prompt (Windows)
   - Type: `docker --version`
   - You should see something like: `Docker version 24.0.0`

## 🚀 Running the Application

### Step 1: Navigate to the Application Folder

1. **Open Terminal/Command Prompt**
2. **Navigate to this application folder:**
   - On Windows: `cd C:\path\to\your\leaf_analysis\`
   - On Mac/Linux: `cd /path/to/your/leaf_analysis/`
   
   *Replace "path/to/your" with the actual path where you extracted this folder*

### Step 2: Start the Application

1. **In your Terminal/Command Prompt, type:**
   ```bash
   docker-compose up --build
   ```

2. **Wait for the setup to complete:**
   - You'll see lots of text scrolling by
   - Wait until you see: `Starting development server at http://0.0.0.0:8000/`
   - This means the application is ready!

### Step 3: Access the Application

1. **Open your web browser** (Chrome, Firefox, Safari, etc.)

2. **Go to one of these addresses:**
   - For User access: `http://127.0.0.1:8000/api/set-cookie/?role=user`
   - For Agronomist access: `http://127.0.0.1:8000/api/set-cookie/?role=agronomist`


### When you're done:

1. **In the Terminal/Command Prompt window** where the application is running
2. **Press `Ctrl + C` (Windows/Linux) or `Cmd + C` (Mac)**
3. **Wait for the application to stop**
4. **To completely shut down, type:**
   ```bash
   docker-compose down
   ```

## 🔄 Restarting the Application

### To run it again later:

1. **Open Terminal/Command Prompt**
2. **Navigate to the application folder** (same as Step 1)
3. **Type:**
   ```bash
   docker-compose up
   ```
   *(No need for --build flag after the first time)*

## ❗ Troubleshooting

### Problem: "docker: command not found"
**Solution:** Docker is not installed or not running
- Make sure Docker Desktop is installed and running
- Look for the Docker whale icon in your system tray/menu bar

### Problem: "Port already in use"
**Solution:** Something else is using port 8000
- Stop any other applications using port 8000
- Or restart your computer

### Problem: "Cannot connect to Docker daemon"
**Solution:** Docker Desktop is not running
- Start Docker Desktop application
- Wait for it to fully start (whale icon should be steady, not animated)

### Problem: Application won't load in browser
**Solution:** 
1. Make sure you see "Starting development server" message in terminal
2. Try these URLs:
   - `http://localhost:8000/api/set-cookie/?role=user`
   - `http://127.0.0.1:8000/api/set-cookie/?role=user`

### Problem: CSS/Styles not loading properly
**Solution:**
1. Stop the application (`Ctrl+C`)
2. Restart with: `docker-compose down && docker-compose up --build`

## 💡 Tips for Success

1. **Always start with the login URLs** (the ones with `/api/set-cookie/?role=user` or `/api/set-cookie/?role=agronomist`)
2. **Don't close the Terminal/Command Prompt window** while using the application
3. **If something goes wrong**, try stopping and restarting the application
4. **Keep Docker Desktop running** while using the application


## 📝 Quick Reference

### Essential Commands:
- **Start application:** `docker-compose up --build` (first time) or `docker-compose up` (subsequent times)
- **Stop application:** `Ctrl+C` then `docker-compose down`
- **Access application:** `http://127.0.0.1:8000/api/set-cookie/?role=user`

### Important URLs:
- **User Dashboard:** `http://127.0.0.1:8000/api/set-cookie/?role=user`
- **Agronomist Dashboard:** `http://127.0.0.1:8000/api/set-cookie/?role=agronomist`

*Remember: Always use the full URL with `/api/set-cookie/?role=` to ensure proper login!* 