REM pyarmor pack main.py
SET COPYCMD=/Y
REM copy  C:\Development\IGBot\dist\*.* C:\Development\IGBot\

REM copy  C:\Development\IGBot\win.spec C:\Development\IGBot\dist\
REM copy  C:\Development\IGBot\*.kv C:\Development\IGBot\dist\
REM xcopy /s  C:\Development\IGBot\data C:\Development\IGBot\dist\data /I
REM xcopy /s  C:\Development\IGBot\userdata C:\Development\IGBot\dist\userdata /I

REM cd dist
pyinstaller win.spec -i data\ml.ico -w --noconsole --clean -y

@RD /S /Q "C:\Development\IGBot\dist\SocialPlannerPro\dist"
@RD /S /Q "C:\Development\IGBot\dist\SocialPlannerPro\env"
@RD /S /Q "C:\Development\IGBot\dist\SocialPlannerPro\.vscode"
@RD /S /Q "C:\Development\IGBot\dist\SocialPlannerPro\.git"
@RD /S /Q "C:\Development\IGBot\dist\SocialPlannerPro\.build"
@RD /S /Q "C:\Development\IGBot\dist\SocialPlannerPro\instructions"
@RD /S /Q "C:\Development\IGBot\dist\SocialPlannerPro\userdata"

cd dist
cd SocialPlannerPro
DEL /S /Q *.py
DEL /S /Q *.spec
DEL /S /Q *.bat
DEL /S /Q *.sh
SIGNTOOL.EXE sign /F C:\Development\IGBot\socialplannerpro.pfx /P p@ssw0rd /tr http://timestamp.digicert.com SocialPlannerPro.exe

cd C:\Users\muzam\AppData\Local\Programs\Inno Setup 6

compil32 /cc "C:\Development\IGBot\instructions\InnoSetupScript.iss"

SIGNTOOL.EXE sign /F C:\Development\IGBot\socialplannerpro.pfx /P p@ssw0rd /tr http://timestamp.digicert.com C:\Development\IGBot\instructions\Output\SocialPlannerProSetup.exe
REM xcopy /i  C:\Development\IGBot\dist\pytransform\_pytransform.dll C:\Development\IGBot\dist\dist\SocialPlannerPro\pytransform\platforms\windows\x86_64\




pyarmor obfuscate --with-license licenses\30aug2020\license.lic --advanced 2 main.py