# PowerShell Script to register the web server to run silently at startup
# Run this script as Administrator to register the task

$ScriptPath = Join-Path $PSScriptRoot "serve.py"
$PythonPath = "C:\Users\khaju\AppData\Local\Python\bin\python.exe"

# 1. Define the action to run serve.py with python silently in the working directory
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument """$ScriptPath""" -WorkingDirectory $PSScriptRoot

# 2. Define the trigger to run automatically at user logon
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# 3. Configure robust task settings to prevent battery saving shutoffs
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 4. Register the Scheduled Task in the background
Register-ScheduledTask -TaskName "DailyCloudAIReleaseServer" `
                       -Action $Action `
                       -Trigger $Trigger `
                       -Settings $Settings `
                       -Description "Runs the local web server silently in the background at startup to host the Cloud & AI Release Intelligence Dashboard." `
                       -Force

Write-Host "Successfully registered DailyCloudAIReleaseServer in Windows Task Scheduler!" -ForegroundColor Green
Write-Host "The web server will now launch silently in the background at startup and remain up at all times!" -ForegroundColor Cyan
