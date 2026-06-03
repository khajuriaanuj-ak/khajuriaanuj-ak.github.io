# PowerShell Script to register a daily Windows Scheduled Task
# Run this script as Administrator to register the task

$ScriptPath = Join-Path $PSScriptRoot "main.py"
$PythonPath = "C:\Users\khaju\AppData\Local\Python\bin\python.exe"

# 1. Define the action to run python and execute main.py with working directory
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument """$ScriptPath""" -WorkingDirectory $PSScriptRoot

# 2. Define the trigger to run daily at 9:00 AM
$Trigger = New-ScheduledTaskTrigger -Daily -At "9:00 AM"

# 3. Configure robust task settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 4. Register the Scheduled Task in the background
Register-ScheduledTask -TaskName "DailyCloudAIReleaseIntelligence" `
                       -Action $Action `
                       -Trigger $Trigger `
                       -Settings $Settings `
                       -Description "Aggregates daily AI-focused releases across AWS, Azure, Google Cloud, OpenAI, Anthropic, Databricks, and Snowflake." `
                       -Force

Write-Host "Successfully scheduled DailyCloudAIReleaseIntelligence in Windows Task Scheduler!" -ForegroundColor Green
Write-Host "The aggregator will run silently in the background daily at 9:00 AM." -ForegroundColor Cyan
