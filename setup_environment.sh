#!/usr/bin/env bash

# Install homebrew if not installed
which brew > /dev/null && echo "Homebrew is already installed..." || /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Install some homebrew packages
brew install python3 wget
# Create a symbolic link for pip
sudo ln -s /usr/local/bin/pip3 /usr/local/bin/pip

# Install JDK 8 for macOS
if [[ $(which java > /dev/null; echo $?) != "0" ]]; then
    pushd ~/Downloads
    wget --no-check-certificate -c --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u171-b11/512cd62ec5174c3487ac17c61aaa89e8/jdk-8u171-macosx-x64.dmg
    hdiutil attach jdk-8u171-macosx-x64.dmg && sudo /usr/sbin/installer -pkg /Volumes/JDK\ 8\ Update\ 171/JDK\ 8\ Update\ 171.pkg -target /
    hdiutil detach /Volumes/JDK\ 8\ Update\ 171/
    rm jdk-8u171-macosx-x64.dmg
    popd
else
    echo "Java is already installed..."
fi

brew install gradle

# Install Android SDK-Tools for macOS
if [[ $(which sdkmanager > /dev/null; echo $?) != "0" ]]; then
    pushd ~/Downloads
    wget https://dl.google.com/android/repository/sdk-tools-darwin-3859397.zip
    unzip sdk-tools-darwin-3859397.zip
    rm sdk-tools-darwin-3859397.zip
    mkdir -p ~/Library/Frameworks/Android && sudo @mv tools ~/Library/Frameworks/Android
    PATH=$PATH:~/Library/Frameworks/Android/tools/bin/ && export PATH
    popd
else
    echo "Android sdkmanager is already installed..."
fi

# Accept all licenses and install Android platform and build tools.
yes | sdkmanager --licenses
sdkmanager "platforms;android-21"
sdkmanager "build-tools;27.0.3"

# Install Crystax NDK 10.3.2 (necessary for python-for-android with python3)
if [ ! -d ~/Library/Frameworks/crystax-ndk-10.3.2 ]; then
    pushd ~/Downloads
    wget https://www.crystax.net/download/crystax-ndk-10.3.2-darwin-x86_64.tar.xz
    tar xf crystax-ndk-10.3.2-darwin-x86_64.tar.xz
    rm crystax-ndk-10.3.2-darwin-x86_64.tar.xz
    sudo mv crystax-ndk-10.3.2 ~/Library/Frameworks
    popd
else
    echo "CrystaX NDK 10.3.2 is already installed..."
fi

# Install cython 0.25.2
pip3 install "cython == 0.25.2"

# Install python-for-android and kivy
pip3 install "python-for-android == 0.6.0"
pip3 install "kivy = 1.10.0"

# Install virtualenv
pip3 install "virtualenv == 16.0.0"

# Install buildozer
pip3 install "buildozer == 0.34"

############################################
# Install stuff for macOS packaging.
############################################

## Install platypus
if [[ $(which platypus > /dev/null; echo $?) != "0" ]]; then
    pushd ~/Downloads
    wget https://sveinbjorn.org/files/software/platypus/platypus5.2.zip
    unzip platypus5.2.zip
    rm platypus5.2.zip
    
    sudo cp Platypus-5.2/Platypus.app/Contents/Resources/platypus_clt /usr/local/bin/
    sudo mv /usr/local/bin/platypus_clt /usr/local/bin/platypus
    
    sudo mkdir -p /usr/local/share/platypus
    sudo cp Platypus-5.2/Platypus.app/Contents/Resources/ScriptExec /usr/local/share/platypus
    sudo chmod +x /usr/local/share/platypus/ScriptExec
    sudo cp -R Platypus-5.2/Platypus.app/Contents/Resources/MainMenu.nib /usr/local/share/platypus
    
    rm -Rf Platypus-5.2
    popd
else
    echo "Platypus is already installed..."
fi

## Install GStreamer
if [[ ! -d /Library/Frameworks/GStreamer.framework ]]; then
    pushd ~/Downloads
    
    # You need both, gstreamer runtime binaries and libs and the development package including the headers.
    
    wget https://gstreamer.freedesktop.org/data/pkg/osx/1.14.0/gstreamer-1.0-devel-1.14.0-x86_64.pkg
    sudo /usr/sbin/installer -pkg gstreamer-1.0-devel-1.14.0-x86_64.pkg -target /
    rm gstreamer-1.0-devel-1.14.0-x86_64.pkg
    
    wget https://gstreamer.freedesktop.org/data/pkg/osx/1.14.0/gstreamer-1.0-1.14.0-x86_64.pkg
    sudo /usr/sbin/installer -pkg gstreamer-1.0-1.14.0-x86_64.pkg -target /
    rm gstreamer-1.0-1.14.0-x86_64.pkg
    
    popd
else
    echo "GStreamer is already installed..."
fi

## Install SDL2 stuff
if [[ ! -d /Library/Frameworks/SDL2.framework ]]; then
    pushd ~/Downloads
    wget https://www.libsdl.org/release/SDL2-2.0.4.dmg
    hdiutil attach SDL2-2.0.4.dmg && sudo cp -R /Volumes/SDL2/SDL2.framework /Library/Frameworks
    hdiutil detach /Volumes/SDL2
    rm SDL2-2.0.4.dmg
    popd
else
    echo "SDL2 is already installed..."
fi

if [[ ! -d /Library/Frameworks/SDL2_image.framework ]]; then
    pushd ~/Downloads
    wget https://www.libsdl.org/projects/SDL_image/release/SDL2_image-2.0.1.dmg
    hdiutil attach SDL2_image-2.0.1.dmg && sudo cp -R /Volumes/SDL2_image/SDL2_image.framework /Library/Frameworks
    hdiutil detach /Volumes/SDL2_image
    rm SDL2_image-2.0.1.dmg
    popd
else
    echo "SDL2_image is already installed..."
fi

if [[ ! -d /Library/Frameworks/SDL2_ttf.framework ]]; then
    pushd ~/Downloads
    wget https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-2.0.14.dmg
    hdiutil attach SDL2_ttf-2.0.14.dmg && sudo cp -R /Volumes/SDL2_ttf/SDL2_ttf.framework /Library/Frameworks
    hdiutil detach /Volumes/SDL2_ttf
    rm SDL2_ttf-2.0.14.dmg
    popd
else
    echo "SDL2_ttf is already installed..."
fi

if [[ ! -d /Library/Frameworks/SDL2_mixer.framework ]]; then
    pushd ~/Downloads
    wget https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-2.0.1.dmg
    hdiutil attach SDL2_mixer-2.0.1.dmg && sudo cp -R /Volumes/SDL2_mixer/SDL2_mixer.framework /Library/Frameworks
    hdiutil detach /Volumes/SDL2_mixer
    rm SDL2_mixer-2.0.1.dmg
    popd
else
    echo "SDL2_mixer is already installed..."
fi

## Install libintl.8.dylib
if [[ ! -f /usr/local/lib/libintl.8.dylib ]]; then
    brew install gettext
    sudo ln -s /usr/local/Cellar/gettext/0.19.8.1/lib/libintl.8.dylib /usr/local/lib/
else
    echo "libintl.8.dylib is already installed..."
fi