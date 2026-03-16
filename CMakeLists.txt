# ============================================================================
# openCFW — Even Realities G2 Custom Firmware Build System
# ============================================================================
#
# This is a build infrastructure SKELETON for the decompiled G2 firmware.
# It defines the correct toolchains, memory maps, and packaging pipeline
# for each of the 4 firmware targets in the EVENOTA package.
#
# STATUS: The decompiled source in src/ is NOT yet compilable.
#   See BUILD_STATUS.md for the work required to make each target build.
#
# TARGETS:
#   g2_main_firmware    — Apollo510b main application (ARM Cortex-M55)
#   g2_bootloader       — Apollo510b bootloader (ARM Cortex-M55)
#   g2_case_firmware    — Case MCU firmware (ARM Cortex-M0+, STM32-like)
#   g2_touch_firmware   — Touch controller firmware (ARM Cortex-M0, CY8C4046FNI)
#
# NON-BUILDABLE COMPONENTS (binary-only, pass-through to EVENOTA):
#   firmware/codec.bin      — GX8002B audio codec (proprietary, byte-identical across versions)
#   firmware/ble_em9305.bin — EM9305 BLE radio patch (proprietary, byte-identical across versions)
#
# USAGE:
#   cmake -B build -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi-gcc.cmake
#   cmake --build build --target g2_main_firmware
#   cmake --build build --target evenota_package
#
# ============================================================================

cmake_minimum_required(VERSION 3.20)
project(openCFW
    VERSION 0.1.0
    LANGUAGES C ASM
    DESCRIPTION "Even Realities G2 Custom Firmware"
)

# ── Toolchain check ──
if(NOT CMAKE_C_COMPILER_ID MATCHES "GNU|Clang|IAR")
    message(FATAL_ERROR
        "ARM cross-compiler required. Install with:\n"
        "  brew install arm-none-eabi-gcc   (macOS)\n"
        "  sudo apt install gcc-arm-none-eabi  (Linux)\n"
        "Then configure with:\n"
        "  cmake -B build -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi-gcc.cmake"
    )
endif()

# ── SDK paths ──
set(AMBIQ_SDK    ${CMAKE_SOURCE_DIR}/sdks/AmbiqSuite_v5)
set(STM32_SDK    ${CMAKE_SOURCE_DIR}/sdks/STM32CubeL0)
set(NRF5_SDK     ${CMAKE_SOURCE_DIR}/sdks/nRF5_SDK_17.1.0_ddde560)
set(NPMX_SDK     ${CMAKE_SOURCE_DIR}/sdks/npmx)
set(LVGL_SDK     ${CMAKE_SOURCE_DIR}/sdks/lvgl_v9.3)
set(FREETYPE_SDK ${CMAKE_SOURCE_DIR}/sdks/freetype)
set(LC3_SDK      ${CMAKE_SOURCE_DIR}/sdks/lc3)
set(ICM_SDK      ${CMAKE_SOURCE_DIR}/sdks/ICM45608)

# ── Source directories ──
set(SRC_ROOT     ${CMAKE_SOURCE_DIR}/src)
set(FW_ROOT      ${SRC_ROOT}/platform/apollo510b/main_firmware)
set(BL_ROOT      ${SRC_ROOT}/platform/apollo510b/bootloader)
set(CASE_ROOT    ${SRC_ROOT}/peripherals/case_mcu)
set(TOUCH_ROOT   ${SRC_ROOT}/peripherals/touch_controller)

# ============================================================================
# Target 1: G2 Main Firmware (Apollo510b ARM Cortex-M55)
# ============================================================================
# Memory map:
#   Flash: 0x00438000 (load address, ~3.1 MB application region)
#   SRAM:  0x20000000 – 0x2007FFFF (512 KB, SP=0x2007FB00)
# ============================================================================

file(GLOB_RECURSE G2_MAIN_SOURCES
    ${FW_ROOT}/app/*.c
    ${FW_ROOT}/audio/*.c
    ${FW_ROOT}/codec/*.c
    ${FW_ROOT}/comms/*.c
    ${FW_ROOT}/driver/*.c
    ${FW_ROOT}/firmware/*.c
    ${FW_ROOT}/framework/*.c
    ${FW_ROOT}/hal/*.c
    ${FW_ROOT}/platform/*.c
    ${FW_ROOT}/product/*.c
    ${FW_ROOT}/rtos/*.c
    ${FW_ROOT}/storage/*.c
    ${FW_ROOT}/system/*.c
    ${FW_ROOT}/utils/*.c
)
# Exclude stub _unclassified.c files
list(FILTER G2_MAIN_SOURCES EXCLUDE REGEX "_unclassified\\.c$")

file(GLOB_RECURSE G2_THIRDPARTY_SOURCES
    ${FW_ROOT}/third_party/*.c
)

add_executable(g2_main_firmware
    ${G2_MAIN_SOURCES}
    ${G2_THIRDPARTY_SOURCES}
)

target_include_directories(g2_main_firmware PRIVATE
    ${FW_ROOT}
    ${FW_ROOT}/hal
    ${FW_ROOT}/driver
    ${AMBIQ_SDK}/CMSIS/AmbiqMicro/Include
    ${AMBIQ_SDK}/mcu/apollo510/hal
    ${AMBIQ_SDK}/mcu/apollo510/hal/mcu
    ${AMBIQ_SDK}/components/graphics/NemaGFX_SDK/headers/include/tsi/NemaGFX
    ${AMBIQ_SDK}/components/graphics/NemaGFX_SDK/headers/include/tsi/NemaDC
    ${AMBIQ_SDK}/components/graphics/NemaGFX_SDK/headers/include/tsi/NemaVG
    ${LVGL_SDK}/src
    ${FREETYPE_SDK}/include
    ${LC3_SDK}/include
    ${ICM_SDK}/c_driver/icm45605/imu
    ${NPMX_SDK}
    ${NPMX_SDK}/drivers/include
)

target_compile_definitions(g2_main_firmware PRIVATE
    APOLLO510_FPGA=0
    AM_PART_APOLLO510
    AM_PACKAGE_BGA
    configUSE_PREEMPTION=1
    LV_CONF_INCLUDE_SIMPLE
    LV_OBJ_STYLE_CACHE=1
    # The firmware was built with IAR — GCC needs these compatibility defines
    __ICCARM__=0
    __GNUC__=1
)

target_compile_options(g2_main_firmware PRIVATE
    -mcpu=cortex-m55
    -mthumb
    -mfloat-abi=hard
    -mfpu=fpv5-d16
    -ffunction-sections
    -fdata-sections
    -Wall
    -Os
)

target_link_options(g2_main_firmware PRIVATE
    -T ${CMAKE_SOURCE_DIR}/linker/apollo510b_main.ld
    -mcpu=cortex-m55
    -mthumb
    -mfloat-abi=hard
    -mfpu=fpv5-d16
    -Wl,--gc-sections
    -Wl,-Map=g2_main_firmware.map
    --specs=nosys.specs
)

# NemaGFX is binary-only
target_link_libraries(g2_main_firmware PRIVATE
    ${AMBIQ_SDK}/components/graphics/NemaGFX_SDK/libraries/lib_nema_apollo5x_nemagfx.a
    ${AMBIQ_SDK}/components/graphics/NemaGFX_SDK/extensions/gpu_patch.a
)

# ============================================================================
# Target 2: G2 Bootloader (Apollo510b ARM Cortex-M55)
# ============================================================================
# Memory map:
#   Flash: 0x00410000 (~148 KB bootloader region)
#   Hands off to main app at 0x00438000 via VTOR relocation
# ============================================================================

file(GLOB_RECURSE G2_BL_SOURCES
    ${BL_ROOT}/*.c
)
list(FILTER G2_BL_SOURCES EXCLUDE REGEX "_unclassified\\.c$")

add_executable(g2_bootloader ${G2_BL_SOURCES})

target_include_directories(g2_bootloader PRIVATE
    ${BL_ROOT}
    ${AMBIQ_SDK}/CMSIS/AmbiqMicro/Include
    ${AMBIQ_SDK}/mcu/apollo510/hal
    ${AMBIQ_SDK}/mcu/apollo510/hal/mcu
)

target_compile_definitions(g2_bootloader PRIVATE
    AM_PART_APOLLO510
    BOOTLOADER=1
)

target_compile_options(g2_bootloader PRIVATE
    -mcpu=cortex-m55
    -mthumb
    -mfloat-abi=hard
    -mfpu=fpv5-d16
    -Os
    -ffunction-sections
    -fdata-sections
)

target_link_options(g2_bootloader PRIVATE
    -T ${CMAKE_SOURCE_DIR}/linker/apollo510b_bootloader.ld
    -mcpu=cortex-m55
    -mthumb
    -Wl,--gc-sections
    --specs=nosys.specs
)

# ============================================================================
# Target 3: G2 Case MCU Firmware (ARM Cortex-M0+, STM32-like)
# ============================================================================
# Memory map:
#   Flash: 0x08000000 (STM32 convention)
#   SRAM:  0x20000000 (SP=0x20002C88, ~11 KB)
# ============================================================================

file(GLOB_RECURSE G2_CASE_SOURCES
    ${CASE_ROOT}/*.c
)
list(FILTER G2_CASE_SOURCES EXCLUDE REGEX "_unclassified\\.c$")

add_executable(g2_case_firmware ${G2_CASE_SOURCES})

target_include_directories(g2_case_firmware PRIVATE
    ${CASE_ROOT}
    # STM32 HAL — exact part TBD (L0 series based on vector table analysis)
    ${STM32_SDK}/Drivers/CMSIS/Include
    ${STM32_SDK}/Drivers/CMSIS/Device/ST/STM32L0xx/Include
    ${STM32_SDK}/Drivers/STM32L0xx_HAL_Driver/Inc
)

target_compile_definitions(g2_case_firmware PRIVATE
    STM32L053xx
    USE_HAL_DRIVER
)

target_compile_options(g2_case_firmware PRIVATE
    -mcpu=cortex-m0plus
    -mthumb
    -Os
    -ffunction-sections
    -fdata-sections
)

target_link_options(g2_case_firmware PRIVATE
    -T ${CMAKE_SOURCE_DIR}/linker/stm32_case.ld
    -mcpu=cortex-m0plus
    -mthumb
    -Wl,--gc-sections
    --specs=nosys.specs
)

# ============================================================================
# Target 4: Touch Controller Firmware (ARM Cortex-M0, CY8C4046FNI)
# ============================================================================
# Memory map:
#   Flash: 0x00000000 (Cypress PSoC4)
#   SRAM:  0x20000000 (SP=0x20002000, 8 KB)
# ============================================================================

file(GLOB_RECURSE G2_TOUCH_SOURCES
    ${TOUCH_ROOT}/*.c
)
list(FILTER G2_TOUCH_SOURCES EXCLUDE REGEX "_unclassified\\.c$")

add_executable(g2_touch_firmware ${G2_TOUCH_SOURCES})

target_compile_options(g2_touch_firmware PRIVATE
    -mcpu=cortex-m0
    -mthumb
    -Os
    -ffunction-sections
    -fdata-sections
)

target_link_options(g2_touch_firmware PRIVATE
    -T ${CMAKE_SOURCE_DIR}/linker/cy8c4046fni.ld
    -mcpu=cortex-m0
    -mthumb
    -Wl,--gc-sections
    --specs=nosys.specs
)

# ============================================================================
# EVENOTA Packaging Pipeline
# ============================================================================
# Assembles the 6-component EVENOTA package from individual firmware binaries.
# Components 5 (codec) and 6 (BLE EM9305) are binary pass-through from
# the reference firmware since they're proprietary and byte-identical.
# ============================================================================

add_custom_target(evenota_package
    COMMAND ${CMAKE_COMMAND} -E echo "Building EVENOTA package..."
    COMMAND python3 ${CMAKE_SOURCE_DIR}/tools/build_evenota.py
        --main      $<TARGET_FILE:g2_main_firmware>
        --bootloader $<TARGET_FILE:g2_bootloader>
        --touch     $<TARGET_FILE:g2_touch_firmware>
        --case      $<TARGET_FILE:g2_case_firmware>
        --codec     ${CMAKE_SOURCE_DIR}/firmware_blobs/firmware_codec.bin
        --ble       ${CMAKE_SOURCE_DIR}/firmware_blobs/firmware_ble_em9305.bin
        --output    ${CMAKE_BINARY_DIR}/g2_openCFW.evenota
        --version   ${PROJECT_VERSION}
    DEPENDS g2_main_firmware g2_bootloader g2_touch_firmware g2_case_firmware
    COMMENT "Packaging EVENOTA firmware image"
)
