Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "C:\stuff\source\PulseWork\setup\setup_inactivity_monitor.bat" & Chr(34), 0
Set WshShell = Nothing
