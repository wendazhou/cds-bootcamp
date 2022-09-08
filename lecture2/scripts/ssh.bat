@echo off
setlocal

:: Forwards the ssh command to the WSL ssh command

:: OpenSSH on Windows does not support connection multiplexing (ControlMaster)
:: which makes it significantly more difficult and annoying to connect to
:: servers which require interactive authentication.
:: Instead, we ask VSCode to forward the SSH command to the linux counterpart.

:: Note: this script additionally strips the -F argument (config file)
:: from the list of arguments, as the Windows path given will not be
:: recognized by the linux executable.

set "args="

:parse
if "%~1" neq "" (
    if "%~1" == "-F" (
        shift /1 & shift /1
        goto :parse
    )
    set args=%args% %1
    shift /1
    goto :parse
)

@echo on
C:\Windows\system32\wsl.exe ssh %args%