# WebRTC Audioprocessing
## Introduction
WebRTC repo contains a very useful audio processing module, which contains very useful tools such as Acoustic Echo Canceller, Sampler rate converter, Automatic Gain Control, Channel downmixer etc.,
If you want to use just the audio processing module of WebRTC without the other bloat, then the challenges are as follows.
- There is no simple way to build audio processing library and all its dependencies in a single binary.
- WebRTC officially supports only clang toolchain. Integrating a clang binary with a Windows or MacOS app using MSVC or XCode toolchain is not straight forward. If you try to build WebRTC for MSVC or XCode toolchain then you will run into a lot of build errors.
- WebRTC build system is based on Ninja/GN which is very difficult to debug build errors for users not familiar with it.

This repo tries to solve the above problem by using a simple CMake based system that builds only those source files required for audio processing module library. Since this is based cmake you are free to use your own toolchain.

## Building
The below points mention the steps for building the WebRTC release version M124, the latest stable release while writing this document. The list of WebRTC releases and its branch name is published [here](https://chromiumdash.appspot.com/branches) by the chromium team.

- Install the WebRTC developer pre-requisite softwares and tools as suggested [here](https://webrtc.googlesource.com/src/+/main/docs/native-code/development/prerequisite-sw/)
- Fetch the latest webrtc src by running the following commands from the root folder of this repository.
```
fetch --nohooks webrtc
gclient sync
```
- Checkout the branch corresponding to WebRTC release that we want to build. For example to checkout code corresponding to release M124, we need to checkout the branch `branch-heads/6367`
```
cd src
git checkout branch-heads/6367
```
- Generate the WebRTC GN build files.
```
gn gen out/Default
```
- Now let's build the audio processing library, using cmake from the root folder of this repo
```
cd ..
mkdir build
cd build
cmake ..
cmake --build . --config Release
```
