pyarmor obfuscate --with-license licenses\2020\license.lic --advanced 2 main.py

SET COPYCMD=/Y

copy  C:\Development\IGBot\winsg.spec C:\Development\IGBot\dist\
copy  C:\Development\IGBot\*.kv C:\Development\IGBot\dist\
copy  C:\Development\IGBot\_pytransform.dll C:\Development\IGBot\dist\
xcopy /s  C:\Development\IGBot\data C:\Development\IGBot\dist\data /I
xcopy /s  C:\Development\IGBot\userdata C:\Development\IGBot\dist\userdata /I
xcopy /s  C:\Development\IGBot\instagram_private_api C:\Development\IGBot\dist\instagram_private_api /I
xcopy /s  C:\Development\IGBot\instagram_web_api C:\Development\IGBot\dist\instagram_web_api /I

cd dist
pyinstaller winsg.spec -i data\sg.ico -w --noconsole --clean -y --paths DIR

@RD /S /Q "C:\Development\IGBot\dist\dist\SocialGrowthApi\dist"
@RD /S /Q "C:\Development\IGBot\dist\dist\SocialGrowthApi\env"
@RD /S /Q "C:\Development\IGBot\dist\dist\SocialGrowthApi\.vscode"
@RD /S /Q "C:\Development\IGBot\dist\dist\SocialGrowthApi\.git"
@RD /S /Q "C:\Development\IGBot\dist\dist\SocialGrowthApi\.build"
@RD /S /Q "C:\Development\IGBot\dist\dist\SocialGrowthApi\instructions"

set folder="C:\Development\IGBot\dist\dist\SocialGrowthApi\userdata"
cd /d %folder%
for /F "delims=" %%i in ('dir /b') do (rmdir "%%i" /s/q || del "%%i" /s/q)
REM @RD /S /Q "C:\Development\IGBot\dist\dist\SocialGrowthApi\userdata"



set folder="C:\Development\IGBot\dist\dist\SocialGrowthApi"
cd /d %folder%

DEL /Q *.py
DEL /S /Q *.spec
DEL /S /Q *.bat
DEL /S /Q *.sh
SIGNTOOL.EXE sign /F C:\Development\IGBot\instructions\socialplannerpro.pfx /P p@ssw0rd /tr http://timestamp.digicert.com SocialGrowthApi.exe


cd C:\Users\muzam\AppData\Local\Programs\Inno Setup 6

compil32 /cc "C:\Development\IGBot\instructions\InnoSetupScriptsg.iss"

SIGNTOOL.EXE sign /F C:\Development\IGBot\instructions\socialplannerpro.pfx /P p@ssw0rd /tr http://timestamp.digicert.com C:\Development\IGBot\instructions\Output\SocialGrowthApiSetup.exe
REM xcopy /i  C:\Development\IGBot\dist\pytransform\_pytransform.dll C:\Development\IGBot\dist\dist\SocialGrowthApi\pytransform\platforms\windows\x86_64\

REM SocialGrowthApi.exe



