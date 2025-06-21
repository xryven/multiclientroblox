# 🚀 Multiclient Roblox Mutex Unlocker
![Multi Roblox instance unlocker](https://img.shields.io/badge/Multi-Roblox_instance_unlocker-black?style=flat) ![Complete freeware](https://img.shields.io/badge/Complete-freeware-black?style=flat) ![Adfree](https://img.shields.io/badge/Adfree-black?style=flat) ![Python](https://img.shields.io/badge/Python-yellow?style=flat)



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
