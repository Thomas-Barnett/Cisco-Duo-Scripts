@echo off
set LOGFILE=C:\Windows\Temp\duo_install.log

echo ====================================== >> %LOGFILE%
echo %date% %time% Starting Duo deployment >> %LOGFILE%

REM Check if Duo is already installed
IF EXIST "C:\Program Files\Duo Security\DuoCredProv\DuoCredProv.dll" (
    echo Duo already installed. Exiting. >> %LOGFILE%
    exit /b 0
)

echo Installing VC++... >> %LOGFILE%
\\lab.local\SYSVOL\lab.local\scripts\duo\VC_redist.x64.exe /install /quiet /norestart >> %LOGFILE% 2>&1

echo Installing Duo... >> %LOGFILE%
\\lab.local\SYSVOL\lab.local\scripts\duo\duo-win-login-5.2.1.exe /S /V" /qn IKEY="xxxxxxxxxxx" SKEY="xxxxxxxxxxxxxxxx" HOST="api-xxxxxxxxxxxx.duosecurity.com" AUTOPUSH="#1" FAILOPEN="#0" SMARTCARD="#0" RDPONLY="#0"" >> %LOGFILE% 2>&1

echo %date% %time% Finished Duo deployment >> %LOGFILE%
exit /b 0