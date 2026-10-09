' UNEX OS - Silent Background Launcher for Windows
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strPath = fso.GetParentFolderName(WScript.ScriptFullName)

' Execute python daemon silently (0 = hide window)
WshShell.Run """" & strPath & "\.venv\Scripts\python.exe"" """ & strPath & "\scripts\unex_daemon.py"" start", 0, False
