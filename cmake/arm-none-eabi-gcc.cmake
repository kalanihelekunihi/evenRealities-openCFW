# ============================================================================
# ARM Cross-Compilation Toolchain File for openCFW
# ============================================================================
# Usage: cmake -B build -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi-gcc.cmake
#
# Prerequisites:
#   macOS:  brew install arm-none-eabi-gcc
#   Linux:  sudo apt install gcc-arm-none-eabi
#   Manual: https://developer.arm.com/downloads/-/gnu-rm
# ============================================================================

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

# Find the toolchain
find_program(ARM_CC arm-none-eabi-gcc)
if(NOT ARM_CC)
    message(FATAL_ERROR
        "arm-none-eabi-gcc not found. Install with:\n"
        "  brew install arm-none-eabi-gcc  (macOS)\n"
        "  sudo apt install gcc-arm-none-eabi  (Linux)"
    )
endif()

set(CMAKE_C_COMPILER   arm-none-eabi-gcc)
set(CMAKE_ASM_COMPILER arm-none-eabi-gcc)
set(CMAKE_OBJCOPY      arm-none-eabi-objcopy)
set(CMAKE_OBJDUMP      arm-none-eabi-objdump)
set(CMAKE_SIZE         arm-none-eabi-size)

# Don't try to link test executables during toolchain detection
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

# Search paths
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
