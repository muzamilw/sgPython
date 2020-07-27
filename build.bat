pyarmor obfuscate --with-license licenses\30aug2020\license.lic --advanced 2 main.py

SET COPYCMD=/Y
REM copy  C:\Development\IGBot\dist\*.* C:\Development\IGBot\

copy  C:\Development\IGBot\win.spec C:\Development\IGBot\dist\
copy  C:\Development\IGBot\*.kv C:\Development\IGBot\dist\
copy  C:\Development\IGBot\_pytransform.dll C:\Development\IGBot\dist\
copy  C:\Development\IGBot\pytransform.pyd C:\Development\IGBot\dist\
xcopy /s  C:\Development\IGBot\data C:\Development\IGBot\dist\data /I
xcopy /s  C:\Development\IGBot\userdata C:\Development\IGBot\dist\userdata /I

cd dist
pyinstaller win.spec -i data\ml.ico -w --noconsole --clean -y --paths DIR

REM @RD /S /Q "C:\Development\IGBot\dist\dist\SocialPlannerPro\dist"
REM @RD /S /Q "C:\Development\IGBot\dist\dist\SocialPlannerPro\env"
REM @RD /S /Q "C:\Development\IGBot\dist\dist\SocialPlannerPro\.vscode"
REM @RD /S /Q "C:\Development\IGBot\dist\dist\SocialPlannerPro\.git"
REM @RD /S /Q "C:\Development\IGBot\dist\dist\SocialPlannerPro\.build"
REM @RD /S /Q "C:\Development\IGBot\dist\dist\SocialPlannerPro\instructions"
REM @RD /S /Q "C:\Development\IGBot\dist\dist\SocialPlannerPro\userdata"

cd dist
cd SocialPlannerPro
REM DEL /S /Q *.py
REM DEL /S /Q *.spec
REM DEL /S /Q *.bat
REM DEL /S /Q *.sh
REM SIGNTOOL.EXE sign /F C:\Development\IGBot\instructions\socialplannerpro.pfx /P p@ssw0rd /tr http://timestamp.digicert.com SocialPlannerPro.exe

REM cd C:\Users\muzam\AppData\Local\Programs\Inno Setup 6

REM compil32 /cc "C:\Development\IGBot\instructions\InnoSetupScript.iss"

REM SIGNTOOL.EXE sign /F C:\Development\IGBot\socialplannerpro.pfx /P p@ssw0rd /tr http://timestamp.digicert.com C:\Development\IGBot\instructions\Output\SocialPlannerProSetup.exe
REM xcopy /i  C:\Development\IGBot\dist\pytransform\_pytransform.dll C:\Development\IGBot\dist\dist\SocialPlannerPro\pytransform\platforms\windows\x86_64\

SocialPlannerPro.exe



REM pyarmor obfuscate --with-license licenses\30aug2020\license.lic --advanced 2 main.py