# openCFW Build Status

## Overview

The build infrastructure targets 4 firmware components that are assembled into a single
EVENOTA package for OTA delivery to the G2 glasses. Two additional components (codec and
BLE radio) are proprietary binary blobs that pass through unchanged.

```
cmake -B build -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi-gcc.cmake
cmake --build build --target evenota_package
```

## Target Status

| Target | Architecture | Status | Blocking Issues |
|--------|-------------|--------|-----------------|
| `g2_main_firmware` | Apollo510b Cortex-M55 | **Not compilable** | See § 1 |
| `g2_bootloader` | Apollo510b Cortex-M55 | **Not compilable** | See § 2 |
| `g2_case_firmware` | STM32 Cortex-M0+ | **Not compilable** | See § 3 |
| `g2_touch_firmware` | CY8C4046FNI Cortex-M0 | **Not compilable** | See § 4 |
| `build_evenota.py` | Host Python | **Ready** | Packaging works |
| Linker scripts | All 4 targets | **Ready** | Memory maps correct |
| Toolchain file | CMake | **Ready** | Detects arm-none-eabi-gcc |

## Prerequisites

```bash
# macOS
brew install cmake arm-none-eabi-gcc

# Linux (Ubuntu/Debian)
sudo apt install cmake gcc-arm-none-eabi

# Manual
# Download from https://developer.arm.com/downloads/-/gnu-rm
```

## 1. Main Firmware (g2_main_firmware)

**Source files:** 228 first-party + 95 third-party = 323 total
**Target:** Apollo510b ARM Cortex-M55, load at 0x00438000

### What's ready
- [x] All source files organized into functional directories
- [x] All decompiler variable names replaced with descriptive names
- [x] SDK register headers for all peripheral ICs
- [x] Linker script with correct memory map
- [x] CMake target with correct compiler flags (-mcpu=cortex-m55)
- [x] NemaGFX binary library linked

### What's blocking compilation

1. **No struct definitions** — The decompiled code accesses struct fields via pointer arithmetic:
   ```c
   // Current (decompiled):
   *(uint32_t *)(ble_state + 0x10) = conn_handle;

   // Needed (compilable):
   ble_state->conn_handle = conn_handle;
   ```
   ~7,200 cast-dereference patterns need struct definitions. The lv_obj_t and
   nema_cmdlist_t layouts are documented in firmware_defs.h but not yet applied.

2. **No function prototypes** — Functions are defined but not declared in headers.
   The compiler needs forward declarations for all ~5,300 functions.

3. **Global variable declarations** — The 201 remaining `str_` data pointers and
   ~4,900 `_data_`/`_state_`/`_flag_` globals need proper `extern` declarations.

4. **MERGE_4_4 return types** — 1,244 functions return `uint64_t` via the MERGE
   macro instead of proper struct returns. Signatures need updating.

5. **Goto-based control flow** — 681 goto labels represent decompiler artifacts
   that should ideally be restructured into loops/conditionals, though they ARE
   valid C.

6. **Missing startup code** — No Reset_Handler, SystemInit, or C runtime init
   (`__libc_init_array`, data/bss initialization). Need startup_apollo510b.s.

7. **FreeRTOS configuration** — FreeRTOSConfig.h is missing. Need to extract
   configuration from the decompiled RTOS code.

### Estimated work to compile
- Struct definitions: ~40 structs needed (lv_obj_t, nema_cmdlist_t, BLE context, etc.)
- Function prototypes: auto-generatable from existing function definitions
- Startup assembly: ~100 lines (standard Cortex-M55 startup)
- FreeRTOS config: ~50 defines
- **Rough estimate: 2-4 weeks of focused work**

## 2. Bootloader (g2_bootloader)

**Source files:** 29
**Target:** Apollo510b ARM Cortex-M55, load at 0x00410000

### Blocking issues
Same as main firmware (struct definitions, prototypes, startup code), but smaller scope.
The bootloader is simpler: LittleFS, flash driver, OTA state machine, RTOS.

### Estimated work: 1 week

## 3. Case Firmware (g2_case_firmware)

**Source files:** 35
**Target:** STM32L0xx ARM Cortex-M0+, load at 0x08000000

### Additional blocking issues
- **Unknown exact STM32 part** — Inferred as STM32L053C8 from SP address, but not confirmed
- **STM32 HAL driver layer** — The code calls `__HAL_FLASH_SET_LATENCY`, `HAL_DMA_Abort`
  etc. which need the correct STM32CubeL0 HAL driver files linked
- **Peripheral init** — Clock tree, GPIO, I2C, UART configuration is in decompiled form

### Estimated work: 1-2 weeks

## 4. Touch Controller (g2_touch_firmware)

**Source files:** 26
**Target:** CY8C4046FNI ARM Cortex-M0, PSoC4

### Additional blocking issues
- **No Cypress PSoC Creator SDK** — The CY8C4046FNI uses Cypress-specific peripheral
  registers not covered by our SDKs. Would need PSoC Creator or ModusToolbox.
- **CapSense configuration** — The capsense_core.c has complex touch sensing algorithms
  that depend on hardware-specific calibration data.

### Estimated work: 2-3 weeks (plus PSoC SDK acquisition)

## 5. EVENOTA Packaging (build_evenota.py)

**Status: Ready**

The packaging tool implements the complete EVENOTA container format:
- 160-byte outer header with TOC
- Per-entry 128-byte sub-headers
- CRC32C (Castagnoli) checksums
- Component wrapping (preamble for main FW, FWPK for touch, EVEN for case)

```bash
# Test with reference firmware components:
python3 tools/build_evenota.py \
    --main firmware_blobs/ota_s200_firmware_ota.bin \
    --bootloader firmware_blobs/ota_s200_bootloader.bin \
    --touch firmware_blobs/firmware_touch.bin \
    --case firmware_blobs/firmware_box.bin \
    --codec firmware_blobs/firmware_codec.bin \
    --ble firmware_blobs/firmware_ble_em9305.bin \
    --output test_repackage.evenota \
    --version 2.0.7.16
```

## 6. Binary Blobs (pass-through)

These components are proprietary and byte-identical across all firmware versions:

| Component | Size | Notes |
|-----------|------|-------|
| `firmware_codec.bin` | 319,372 bytes | GX8002B audio codec (FWPK + BINH format) |
| `firmware_ble_em9305.bin` | 211,948 bytes | EM9305 BLE radio patch (segmented) |

Place reference copies in `openCFW/firmware_blobs/` for packaging.

## Build Architecture

```
openCFW/
├── CMakeLists.txt              ← Top-level build (this file documents)
├── cmake/
│   └── arm-none-eabi-gcc.cmake ← Cross-compilation toolchain
├── linker/
│   ├── apollo510b_main.ld      ← Main FW: 0x438000, 3.1MB flash, 512KB SRAM
│   ├── apollo510b_bootloader.ld ← Bootloader: 0x410000, 160KB flash
│   ├── stm32_case.ld           ← Case: 0x08000000, 64KB flash, 8KB SRAM
│   └── cy8c4046fni.ld          ← Touch: 0x00000000, 32KB flash, 8KB SRAM
├── firmware_blobs/              ← Binary pass-through components
│   ├── firmware_codec.bin
│   └── firmware_ble_em9305.bin
├── tools/
│   └── build_evenota.py         ← EVENOTA packaging pipeline
├── src/                         ← Decompiled source (not yet compilable)
│   ├── platform/apollo510b/
│   │   ├── main_firmware/       ← 323 source files
│   │   └── bootloader/          ← 29 source files
│   └── peripherals/
│       ├── case_mcu/            ← 35 source files
│       └── touch_controller/    ← 26 source files
└── sdks/                        ← Vendor SDKs (HAL, CMSIS, drivers)
    ├── AmbiqSuite_v5/
    ├── STM32CubeL0/
    ├── lvgl_v9.3/
    ├── npmx/
    └── ...
```

## Roadmap to Compilable Firmware

### Phase 1: Infrastructure (DONE)
- [x] CMake build system with all 4 targets
- [x] Linker scripts with correct memory maps
- [x] Toolchain file for arm-none-eabi-gcc
- [x] EVENOTA packaging tool
- [x] SDK include paths configured

### Phase 2: Header Generation
- [ ] Auto-generate function prototypes from source files
- [ ] Create `extern` declarations for all global variables
- [ ] Create proper `#include` chains between source files

### Phase 3: Struct Recovery
- [ ] Define lv_obj_t struct (layout documented in firmware_defs.h)
- [ ] Define nema_cmdlist_t struct (layout documented in firmware_defs.h)
- [ ] Define BLE connection context struct
- [ ] Define display render context struct
- [ ] Replace *(type*)(ptr+offset) patterns with struct field access

### Phase 4: Startup Code
- [ ] Write startup_apollo510b.s (vector table, C runtime init)
- [ ] Write startup_stm32l0xx.s
- [ ] Write startup_cy8c4046.s
- [ ] Create FreeRTOSConfig.h from decompiled RTOS parameters

### Phase 5: Compilation Fixes
- [ ] Fix MERGE_4_4 return types → proper struct returns
- [ ] Resolve remaining goto labels where possible
- [ ] Add missing type casts for strict compilation
- [ ] Fix IAR-to-GCC compatibility issues

### Phase 6: Testing
- [ ] Binary comparison with reference firmware
- [ ] Flash to hardware and verify boot
- [ ] BLE connectivity test
- [ ] Display rendering test
