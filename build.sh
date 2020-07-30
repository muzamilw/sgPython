python pyarmor obfuscate --with-license licenses/30aug2020/license.lic --advanced 2 main.py


pyarmor pack -x " --exact --exclude env " -s mzapp.spec main.py

cp -R /Users/JanatFarooq/Documents/GitHub/sgPython/mac2.spec /Users/JanatFarooq/Documents/GitHub/sgPython/dist/
cp -R /Users/JanatFarooq/Documents/GitHub/sgPython/ml.icns /Users/JanatFarooq/Documents/GitHub/sgPython/dist/
cp  /Users/JanatFarooq/Documents/GitHub/sgPython/*.kv /Users/JanatFarooq/Documents/GitHub/sgPython/dist/
#cp  /Users/JanatFarooq/Documents/GitHub/sgPython_pytransform.dll /Users/JanatFarooq/Documents/GitHub/sgPython\dist\
#cp  /Users/JanatFarooq/Documents/GitHub/sgPython\pytransform.pyd /Users/JanatFarooq/Documents/GitHub/sgPython\dist\
cp /s  /Users/JanatFarooq/Documents/GitHub/sgPython/data /Users/JanatFarooq/Documents/GitHub/sgPython/dist/data