::Please execute this file on the virtual machine and establish a connection.

@echo off
echo Installing OpenSSH Server...

:: Check if OpenSSH-Server is already installed
powershell -Command "Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*' | ForEach-Object {if ($_.State -eq 'Installed') {exit 0} else {exit 1}}" >nul 2>&1
if %errorlevel% equ 0 (
    echo OpenSSH Server is already installed.
) else (
    echo Installing OpenSSH Server...
    powershell -Command "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"
    echo OpenSSH Server installed successfully.
)

:: Start the OpenSSH Server service
sc config sshd start= auto
net start sshd

if %errorlevel% equ 2 (
    echo OpenSSH Server service is already running.
) else (
    echo OpenSSH Server service started successfully.
)

echo Installation and configuration completed.
pause
