Set WshShell = CreateObject("WScript.Shell")

' === Launch the tray app and agent silently ===
WshShell.Run "C:\stuff\source\heartBeat\launch_monitor.bat", 0, False

' === Schedule hourly checker task silently ===
WshShell.Run "C:\stuff\source\heartBeat\schedule_agent_checker.bat", 0, False

Set WshShell = Nothing