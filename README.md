

# 🛡️ ClamAV Tk 

ClamAV Tk is a graphical user interface (GUI) designed to facilitate the use of [ClamAV](https://www.clamav.net/), an open source antivirus software. This repo is forked and built from [Acosta-gh/clamav-tkinter_PYTHON](https://github.com/Acosta-gh/clamav-tkinter_PYTHON). ClamAV Tk (this repo) is a WIP and not currently stable.

## Features

- Scan files or directories
    
- Scan history
    
- Cloud database update
    

## Requirements

- Python 3.12+
    
- ClamAV
    
- Windows OS

## Installation

1. **Backend**: Download `.msi` installer from ClamAV [website](https://www.clamav.net/downloads), and install. No need for further configuration.

2. **Frontend** (this repo): Download ClamAV Tk GUI `.exe` and run.

3. Check tab `Upgrade` for autoconfiguration.

## Build from source

See `build.bat`.

## Todo

- [ ] apply theme to all pop up windows
- [ ] scan bar popup -> scan frame inside
- [ ] add a Quick Scan
- [ ] re-enable multilanguage UI
- [ ] extract UI strings to a single json provider util
- [ ] break class ClamAVScanner into components

## Icon

Crédito del icono: [diamonjohn en Openclipart](https://openclipart.org/artist/diamonjohn)
