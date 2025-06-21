import win32event,win32api,time
m=win32event.CreateMutex(None,1,"ROBLOX_singletonMutex")
if win32api.GetLastError()!=183:
 print("Mutex blocked")
 try:
  while 1:time.sleep(1)
 except:pass
else:print("Mutex in use")