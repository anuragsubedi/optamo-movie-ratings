# Automation Scripts

This folder contains automation scripts to quickly set up and run the full-stack Movie Ratings platform (Frontend and Backend) without needing to configure complex DevOps infrastructure like Docker.

## macOS & Linux

**1. One-time Setup** (Installs Python/Node packages and migrates the SQLite database):

```bash
./shell_scripts/macos_linux_setup.sh
```

**2. Run the Application**:

```bash
./shell_scripts/macos_linux_run.sh
```

> Running the run script will spin up both Flask and Angular concurrently. You can gracefully stop both servers at the exact same time by simply pressing `CTRL+C` in your terminal.

---

## Windows

**1. One-time Setup** (Installs Python/Node packages and migrates the SQLite database):

```cmd
.\shell_scripts\windows_setup.bat
```

**2. Run the Application**:

```cmd
.\shell_scripts\windows_run.bat
```

> Running this script will spawn two new separate Command Prompt windows (one for the backend port 5001, one for the frontend port 4200). To stop the servers, just close those terminal windows.
