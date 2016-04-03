@ECHO OFF

:choice
set /P c=Do you want to download the latest spritedata.xml [Y/N]?
if /I "%c%" EQU "Y" goto :downloadthatstuff
if /I "%c%" EQU "N" goto :nogoaway
goto :choice


:downloadthatstuff

@echo OFF
echo Downloading latest spritedata...
powershell -Command "Invoke-WebRequest http://rhcafe.us.to/spritexml.php -OutFile reggiedata/spritedata.xml"
echo Done!

:nogoaway
set /P c=Do you want to download the latest category.xml [Y/N]?
if /I "%c%" EQU "Y" goto :downloadthatxml
if /I "%c%" EQU "N" goto :srslygoaway
goto :nogoaway

:downloadthatxml

@echo OFF
echo Downloading latest spritedata...
powershell -Command "Invoke-WebRequest http://rhcafe.us.to/categoryxml.php -OutFile reggiedata/category.xml"
echo Done!
echo Starting Reggie!
cmd /k C:/Python34/python.exe reggie.py

:srslygoaway
@echo OFF
echo Starting Reggie!
cmd /k C:/Python34/python.exe reggie.py