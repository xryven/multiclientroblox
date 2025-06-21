# 🚀 Multiclient Roblox Mutex Unlocker
![Multi Roblox instance](https://img.shields.io/badge/Multi-Roblox_instance-blue?style=flat) ![Freeware](https://img.shields.io/badge/Freeware-yes-green?style=flat)

### 💡 How does it work?  
This script uses the line  
`Mutex mutex = new Mutex(true, "ROBLOX_singletonMutex");`  
to block Roblox’s default mutex, allowing multiple instances.

### ❓ Why should I use this?  
If you're playing a game that isn’t an obby or tycoon, this script can significantly enhance your experience.  
It allows you to run multiple Roblox clients simultaneously (default limit is 1).  
It can also be useful for testing, development, or other purposes.

### ❓ How do I build this to an .EXE?  
Simply build this script to an executable by running:  
`python -m PyInstaller --onefile --noconsole --icon=icon.ico --optimize=2 name.pyw`
The executable will be created in the `dist/` folder.
