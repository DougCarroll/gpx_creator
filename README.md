# GPX Creator

A Python GUI application to create GPX (GPS Exchange Format) files with a simple interface.

## Features

- User-friendly GUI built with tkinter
- Input fields for:
  - Time (defaults to current UTC time)
  - Waypoint (latitude and longitude)
  - Name
- Automatic bounds calculation from waypoint coordinates
- Default symbol set to "WayPoint"
- Generates GPX files matching the template format

## Requirements

- Python 3.6 or higher
- tkinter (GUI library)

## Installation

### macOS

#### Option 1: Using Homebrew (Recommended)

1. Install Homebrew if you don't have it:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Python:
   ```bash
   brew install python3
   ```

3. Verify installation:
   ```bash
   python3 --version
   ```

4. tkinter comes pre-installed with Python on macOS, so no additional steps are needed.

#### Option 2: Using Official Python Installer

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and follow the prompts
3. Make sure to check "Add Python to PATH" during installation
4. tkinter is included with the official Python installer

### Linux

#### Ubuntu/Debian

1. Update package list:
   ```bash
   sudo apt update
   ```

2. Install Python 3 and tkinter:
   ```bash
   sudo apt install python3 python3-tk
   ```

3. Verify installation:
   ```bash
   python3 --version
   ```

#### Fedora/RHEL/CentOS

1. Install Python 3 and tkinter:
   ```bash
   sudo dnf install python3 python3-tkinter
   ```
   Or for older versions using yum:
   ```bash
   sudo yum install python3 python3-tkinter
   ```

2. Verify installation:
   ```bash
   python3 --version
   ```

#### Arch Linux

1. Install Python and tkinter:
   ```bash
   sudo pacman -S python tk
   ```

2. Verify installation:
   ```bash
   python3 --version
   ```

### Windows (PC)

#### Option 1: Using Official Python Installer (Recommended)

1. Download Python from [python.org](https://www.python.org/downloads/)
   - Choose Python 3.x.x (latest stable version)
   - Download the Windows installer (64-bit recommended)

2. Run the installer:
   - **Important**: Check the box "Add Python to PATH" during installation
   - Choose "Install Now" or "Customize installation"
   - If customizing, make sure "tcl/tk and IDLE" is selected (includes tkinter)

3. Verify installation:
   - Open Command Prompt (cmd) or PowerShell
   - Run:
     ```cmd
     python --version
     ```

4. tkinter is included with the official Python installer for Windows.

#### Option 2: Using Microsoft Store

1. Open Microsoft Store
2. Search for "Python 3.x"
3. Install Python from the Microsoft Store
4. tkinter is included with this installation

#### Troubleshooting Windows Installation

If `python` command is not recognized:
1. Add Python to PATH manually:
   - Find Python installation directory (usually `C:\Python3x\` or `C:\Users\YourUsername\AppData\Local\Programs\Python\Python3x\`)
   - Add it to System Environment Variables PATH
2. Or use `py` launcher instead:
   ```cmd
   py gpx_creator.py
   ```

### Verify tkinter Installation

After installing Python, verify tkinter works:

**macOS/Linux:**
```bash
python3 -m tkinter
```

**Windows:**
```cmd
python -m tkinter
```

If a small window appears, tkinter is installed correctly. Close the window to continue.

## Usage

Run the application:

```bash
python gpx_creator.py
```

Fill in the required fields:
- **Time**: UTC timestamp (defaults to current time, click "Now" to update)
- **Waypoint**: Latitude and longitude for the waypoint
- **Name**: Name of the waypoint

Bounds are automatically calculated from the waypoint coordinates, and the symbol defaults to "WayPoint".

Click "Create GPX File" to save your GPX file.

## Example

The generated GPX file follows the same structure as the template file, including:
- Proper XML namespaces
- Metadata with author, copyright, and link information
- Bounds information
- Waypoint with name, description, symbol, and UUID extension

