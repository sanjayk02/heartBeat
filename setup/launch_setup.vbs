Set objShell = CreateObject("Shell.Application")
Set fso = CreateObject("Scripting.FileSystemObject")

' === Path to your PowerShell script ===
ps1Path = "C:\stuff\source\PulseWork\setup\setup.ps1"

' === Check if script exists ===
If Not fso.FileExists(ps1Path) Then
    MsgBox "PowerShell script not found: " & ps1Path, vbCritical, "Error"
    WScript.Quit 1
End If

' === Launch PowerShell script as admin ===
objShell.ShellExecute "powershell.exe", "-ExecutionPolicy Bypass -File """ & ps1Path & """", "", "runas", 1
