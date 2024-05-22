cmake_minimum_required(VERSION 3.10)

# Set your project name
project(AudioProcessingLibrary)

# Include the external .cmake files that lists the common source and header files.
include(sources.cmake)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD_REQUIRED True)

if(UNIX)
  add_definitions(-DWEBRTC_POSIX)
endif()

# iOS
if(IOS)
  add_definitions(-DWEBRTC_MAC -DWEBRTC_IOS)
endif()

# Linux or ChromeOS
if(CMAKE_SYSTEM_NAME STREQUAL "Linux" OR CMAKE_SYSTEM_NAME MATCHES "ChromeOS")
  add_definitions(-DWEBRTC_LINUX)
endif()

# macOS
if(APPLE AND NOT IOS)
  add_definitions(-DWEBRTC_MAC)
endif()

# Windows
if(WIN32)
  set(CMAKE_CXX_STANDARD 20)
  add_definitions(-DWEBRTC_WIN)
  add_definitions(-DNOMINMAX)
  add_definitions(-DWIN32_LEAN_AND_MEAN)
  add_definitions(-D_USE_MATH_DEFINES)
else()
  set(CMAKE_CXX_STANDARD 17)
endif()

add_definitions(-DRTC_DISABLE_CHECK_MSG)
add_definitions(-DWEBRTC_APM_DEBUG_DUMP=0)

message(STATUS "Host System Processor: ${CMAKE_HOST_SYSTEM_PROCESSOR}")

# Definitions copy-pasted from zlib CMakeLists.txt. TODO : Maybe to better to call zlib CMakeLists.txt directly.
if (CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64")
add_definitions(-DINFLATE_CHUNK_SIMD_SSE2)
add_definitions(-DADLER32_SIMD_SSSE3)
add_definitions(-DINFLATE_CHUNK_READ_64LE)
add_definitions(-DCRC32_SIMD_SSE42_PCLMUL)
if (ENABLE_SIMD_AVX512)
  add_definitions(-DCRC32_SIMD_AVX512_PCLMUL)
  add_compile_options(-mvpclmulqdq -msse2 -mavx512f -mpclmul)
else()
  add_compile_options(-msse4.2 -mpclmul)
endif()
add_definitions(-DDEFLATE_SLIDE_HASH_SSE2)
# Required by CPU features detection code.
add_definitions(-DX86_NOT_WINDOWS)
endif()

if ((CMAKE_SYSTEM_PROCESSOR STREQUAL "arm64") OR
(CMAKE_SYSTEM_PROCESSOR STREQUAL "aarch64"))
  add_definitions(-DINFLATE_CHUNK_SIMD_NEON)
  add_definitions(-DADLER32_SIMD_NEON)
  add_definitions(-DINFLATE_CHUNK_READ_64LE)
  add_definitions(-DCRC32_ARMV8_CRC32)
  add_definitions(-DDEFLATE_SLIDE_HASH_NEON)
  # Required by CPU features detection code.
  if (APPLE)
    add_definitions(-DARMV8_OS_MACOS)
  endif()
  if (UNIX AND NOT APPLE)
    add_definitions(-DARMV8_OS_LINUX)
  endif()
  SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -march=armv8-a+crc+crypto")
endif()

if (CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64|amd64|X86_64")
  add_definitions(-DINFLATE_CHUNK_SIMD_SSE2)
  add_definitions(-DADLER32_SIMD_SSSE3)
  add_definitions(-DINFLATE_CHUNK_READ_64LE)
  add_definitions(-DDEFLATE_SLIDE_HASH_SSE2)
  if(WIN32)
    add_definitions(-DX86_WINDOWS)
  else()
    add_definitions(-DX86_NOT_WINDOWS)
  endif()
endif()

find_package(Python3 REQUIRED COMPONENTS Interpreter)

if(Python3_FOUND)
    set(PYTHON_EXECUTABLE ${Python3_EXECUTABLE})
else()
    message(FATAL_ERROR "Python3 not found")
endif()

# Set variables for the script and output directory
set(FT_SCRIPT_PATH "${CMAKE_SOURCE_DIR}/src/experiments/field_trials.py")  # Adjust the path to where the script is located
set(FT_OUTPUT_DIR "${CMAKE_BINARY_DIR}/experiments")
set(FT_OUTPUT_FILE "${FT_OUTPUT_DIR}/registered_field_trials.h")

# Add a custom command that generates the output file
add_custom_command(
    OUTPUT ${FT_OUTPUT_FILE}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${FT_OUTPUT_DIR}
    COMMAND ${CMAKE_COMMAND} -E env PYTHONIOENCODING=utf-8
            ${PYTHON_EXECUTABLE} ${FT_SCRIPT_PATH} header --output ${FT_OUTPUT_FILE}
    DEPENDS ${FT_SCRIPT_PATH}
    COMMENT "Generating registered_field_trials.h"
    VERBATIM
)

# Add a custom target that depends on the output file
add_custom_target(
    GenerateFieldTrialsHeader ALL
    DEPENDS ${FT_OUTPUT_FILE}
)

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}/src/third_party/abseil-cpp/
    ${CMAKE_SOURCE_DIR}/src/third_party/protobuf/src/
    ${CMAKE_SOURCE_DIR}/src/third_party/pffft/src
    ${CMAKE_SOURCE_DIR}/src/third_party/rnnoise/src
    ${CMAKE_SOURCE_DIR}/src/third_party/zlib
    ${CMAKE_BINARY_DIR}
)

if(CMAKE_HOST_SYSTEM_PROCESSOR MATCHES "aarch64|ARM64|arm64")
    add_definitions(-DWEBRTC_ARCH_ARM64)
    add_definitions(-DWEBRTC_HAS_NEON)
    # Add source files for ARM64
    set(SOURCE_FILES
        ${SOURCE_FILES}
        src/common_audio/resampler/sinc_resampler_neon.cc
        src/common_audio/fir_filter_neon.cc
        src/common_audio/signal_processing/cross_correlation_neon.c
        src/common_audio/signal_processing/downsample_fast_neon.c
        src/common_audio/signal_processing/min_max_operations_neon.c
        src/common_audio/third_party/ooura/fft_size_128/ooura_fft_neon.cc
        src/modules/audio_processing/aecm/aecm_core_neon.cc
    )
endif()

if (CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64|amd64|X86_64")
    set(SOURCE_FILES
        ${SOURCE_FILES}
        src/common_audio/resampler/sinc_resampler_sse.cc
        src/common_audio/resampler/sinc_resampler_avx2.cc
        src/common_audio/fir_filter_sse.cc
        src/common_audio/fir_filter_avx2.cc
        src/common_audio/third_party/ooura/fft_size_128/ooura_fft_sse2.cc
        src/modules/audio_processing/aec3/fft_data_avx2.cc
        src/modules/audio_processing/aec3/vector_math_avx2.cc
        src/modules/audio_processing/aec3/adaptive_fir_filter_erl_avx2.cc
        src/modules/audio_processing/aec3/adaptive_fir_filter_avx2.cc
        src/modules/audio_processing/agc2/rnn_vad/vector_math_avx2.cc
    )
    if (APPLE)
        set(SOURCE_FILES
            ${SOURCE_FILES}
            src/modules/audio_processing/aec3/matched_filter_avx2.cc
        )
    endif()
    add_compile_options(
        $<$<OR:$<CXX_COMPILER_ID:GNU>,$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>>:-mavx2>
        $<$<OR:$<CXX_COMPILER_ID:GNU>,$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>>:-mfma>
        $<$<CXX_COMPILER_ID:MSVC>:/arch:AVX2>
    )
endif()

# Add a library target to the project
add_library(audio_processing STATIC ${SOURCE_FILES})

add_dependencies(audio_processing GenerateFieldTrialsHeader)

# Define installation rules for the library
install(TARGETS audio_processing
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)  # for windows dlls

# Define a function to handle the installation of headers
function(install_headers src_path)
  # Remove the last directory from the path to form the destination subdirectory
  string(REGEX REPLACE "/[^/]+$" "" dest_subdir ${src_path})

  install(DIRECTORY ${src_path}
          DESTINATION ${dest_subdir}
          FILES_MATCHING PATTERN "*.h")
endfunction()

# Call the function for each directory
install_headers(src/third_party/abseil-cpp)
install_headers(src/api)
install_headers(src/modules/audio_processing)
install_headers(src/rtc_base)
install_headers(src/common_audio)
