# 🚀 Multiclient Roblox Mutex Unlocker
![Python](https://img.shields.io/badge/Python-yellow?style=flat) ![Github](https://img.shields.io/badge/Github-black?style=flat)
### 💡 How does it work?  
This script uses the line  
`Mutex mutex = new Mutex(true, "ROBLOX_singletonMutex");`  
to block Roblox’s default mutex, allowing multiple instances.

### ❓ Why should I use this?  
If you're playing a game that isn’t an obby or tycoon, this script can significantly enhance your experience.  
It allows you to run multiple Roblox clients simultaneously (default limit is 1).  
It can also be useful for testing, development, or other purposes.

### ❓ How do I build this to an .EXE?  
Simply build this script to an executable by running:<br>
`python -m PyInstaller --onefile --noconsole --icon=icon.ico --optimize=2 name.pyw`<br>
The executable will be created in the `dist/` folder.
