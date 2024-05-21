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

- Install the WebRTC developer pre-requisite softwares and tools as suggested [here](https://webrtc.googlesource.com/src/+/main/docs/native-code/development/prerequisite-sw/). The Windows section of the above page, redirects you to the chromium build steps. In the chromium build steps page, make sure to stop after installing the prerequisites. You need not follow the steps mentioned for downloading and building the chromium source(Obviously duh!).
- Fetch the latest webrtc src by running the following commands from the root folder of this repository. This fetch step might take anywhere between few minutes to few hours depending on your internet connection speed. So be patient. If you try believe the fetch step has hung, then just stop it and re-run the command to restart the download.
```
fetch --nohooks webrtc
gclient sync
```
- Checkout the branch corresponding to WebRTC release that we want to build. For example to checkout code corresponding to release M124, we need to checkout the branch `branch-heads/6367`
```
cd src
git checkout branch-heads/6367
```
- Generate the WebRTC GN build files. This will autogenerate some protobuf source files that are required for building the library.
```
gn gen out/Default
```
- If you using Windows, then apply the below one-line change manually. Planning to submit this upstream, and get rid of this manual step for future versions
```
C:\work\webrtc-audioprocessing\src>git diff
diff --git a/rtc_base/checks.h b/rtc_base/checks.h
index 99fee97d0a..1e243e8ad4 100644
--- a/rtc_base/checks.h
+++ b/rtc_base/checks.h
@@ -475,7 +475,7 @@ RTC_NORETURN RTC_EXPORT void UnreachableCodeReached();
 // remainder is zero.
 template <typename T>
 inline T CheckedDivExact(T a, T b) {
-  RTC_CHECK_EQ(a % b, 0) << a << " is not evenly divisible by " << b;
+  RTC_CHECK_EQ(a % b, 0);
   return a / b;
 }
```
- Now let's build the audio processing library, using cmake from the root folder of this repo
```
cd ..
mkdir build
mkdir install
cd build
cmake -DCMAKE_INSTALL_PREFIX=../install ..
cmake --build . --config Release --target install
```
- The `install` folder will contain the audio processing library(in `lib` subfolder) and the header files needed to use them(in `src` subfolder)

