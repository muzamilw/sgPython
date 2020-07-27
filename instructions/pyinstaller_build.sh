pyinstaller -y --clean --windowed --name SgLabs \
  --exclude-module _tkinter \
  --exclude-module Tkinter \
  --exclude-module enchant \
  --exclude-module twisted \
  /Users/JanatFarooq/Documents/GitHub/sgPython/main.py

pyinstaller -y --clean --windowed SgLabs.spec

pushd dist
hdiutil create ./Touchtracer.dmg -srcfolder touchtracer.app -ov
popd
