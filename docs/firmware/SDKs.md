# Firmware SDK Reference (evidence-grounded)

## Scope

This file documents which public SDK/toolchain families best match each firmware component in this repository’s current evidence set.

## Core conclusions

- **G2 Glasses runtime + bootloader are Ambiq/IAR-based** on Apollo510b, and they share one internal toolchain lineage (`s200_ap510b_iar`).
- **The G2 case (`firmware_box.bin`) is STM32-like** and appears to be a separate STM32-family MCU firmware update flow with A/B bank selection.
- **R1 Nordic assets are Nordic DFU-family artifacts** (SoftDevice/bootloader split with FE59 + MCUmgr), not an application image embedded in the G2 EVENOTA payload.
- **EM9305/codec/touch updates are vendor-specific sidecar firmware paths** with non-Nordic wrapper formats and do not match Nordic SDK app-image conventions.
- **No ESP-family SDK signal is present** for these firmware streams after re-checking the actual binaries and wrapper metadata.

## Public SDK families to inspect

- **Ambiq SDK:** [AmbiqSuite SDK](https://ambiq.com/ambiqsuite-sdk/), [Ambiq Apollo 510 Family documentation](https://ambiq.com/apollo510b/)
- **Nordic (nRF5-family legacy + MCUboot/DFU ecosystem):** [Nordic nRF5 SDK (legacy)](https://www.nordicsemi.com/Products/Development-software/nRF5-SDK/Download), [nRF5 SDK-to-nRF Connect migration note](https://devzone.nordicsemi.com/nrf-connect/nrf-connect-sdk), [nRF Connect SDK / Zephyr](https://www.nordicsemi.com/Products/Development-software/nrf-connect-sdk), [nRF5 DFU + mcumgr docs](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/services/services/mcumgr.html)
- **Vendor component toolchains (no full public stack mapping from binaries yet):** EM Microelectronics EM9305 patch workflow appears vendor-provided; NationalChip GX8002B BINH/FWPK flow appears vendor-specific; Cypress/Infineon CY8C4046FNI FWPK flow appears PSoC-family DFU-specific.

## Per-component SDK / toolchain mapping (current evidence)

### G2 Glasses (Ambiq domain)

- **`ota_s200_firmware_ota.bin` (main app)**
  - Target: **Ambiq Apollo510b**
  - Inference: **Ambiq SDK + IAR Embedded Workbench workflow**
  - Evidence: strings/source-path markers include `D:\01_workspace\s200_ap510b_iar`, Ambiq HAL symbols (`am_hal_*`, `am_devices_*`), Cordio/FreeRTOS/LittleFS layout.
  - Confidence: **High**

- **`ota_s200_bootloader.bin` (bootloader)**
  - Target: **Ambiq Apollo510b**
  - Inference: **same Ambiq/IAR toolchain lineage as main app**
  - Evidence: shared bootloader source path `s200_ap510b_iar`, raw ARM image and VTOR handoff flow.
  - Confidence: **High**

- **`firmware_ble_em9305.bin`**
  - Target: **EM Microelectronics EM9305 BLE coprocessor**
  - Inference: **Vendor-side coprocessor patch workflow** (record-based HCI update), not Nordic app-image/SoftDevice packaging.
  - Publicly released source/installer: **No direct public download found** via unauthenticated browsing.
  - Public EM Microelectronics references consistently point SDK/tooling access through EMDeveloper support forum areas (`software-development-kit.50`), and those pages appear account-gated. EM9304 SOC documentation publicly confirms this same delivery pattern.
  - Publicly available EM9304 SDK materials show a vendor workflow based on Synopsys MetaWare-style project tooling plus EM `.emp` patch project structure, suggesting EM9305 is likely similar (tooling + patch artifacts, not a fully open-source stack).
  - `file(1)` identifies this blob as an Intel ia64 COFF-like container and the payload is a fixed 4-record patch written into EM9305 flash ranges (`0x00300000` base), consistent with vendor-side radio patch tooling rather than a public app source package.
  - ISA: **ARC EM (ARCv2)**, NOT ARM. The EM9305 uses a Synopsys DesignWare ARC EM processor core. ARM disassembly produces invalid results.
  - NVM patch format fully decoded: 4 records (config 224B, params 656B, FHDR 56B, main patch 210KB), 29 erase pages, 14 HCI vendor-specific commands documented.
  - Confidence: **High**

- **`firmware_codec.bin`**
  - Target: **NationalChip GX8002B**
  - Inference: **Vendor BINH/FWPK serial bootloader format**, not Nordic/Nordic SDK image format.
  - Confidence: **High**

- **`firmware_touch.bin`**
  - Target: **Cypress/Infineon CY8C4046FNI (PSoC4)**
  - Inference: **Vendor PSoC DFU flow (FWPK + row-style flash update)**, not Nordic nRF SDK.
  - Confidence: **High**

### G2 Case

- **`firmware_box.bin`**
  - Target: **STM32L0xx ARM Cortex-M0+ (confirmed L0 series)**
  - Inference: **STM32CubeL0 HAL + FreeRTOS (CMSIS-RTOS2 wrapper)**
  - Evidence: GPIO base `0x50000000` confirms L0 series (not F0/G0). Flash base `0x08000000`, dual-bank OTA with A/B partition. 414 functions fully mapped (410 HIGH, 4 MEDIUM). FreeRTOS kernel internals, STM32 HAL UART/I2C/Flash/GPIO/Timer confirmed via STM32CubeL0 SDK cross-reference. Board B200, FW 1.2.54. BIT-banged I2C for YHM2510 communication.
  - Confidence: **High** for STM32L0 family; **Medium** for exact part number (likely STM32L071xx/L081xx based on dual-bank flash).

### R1 Ring (separate Nordic domain)

- **`B210_*` Nordic DFU artifacts (`bootloader.bin`, `softdevice.bin`)**
  - Target: **Nordic nRF5x ring-side stack (S140 SoftDevice layout, nRF52840-class candidate)**
  - Inference: **Nordic legacy nRF5-DFU-era workflow** (B210 naming + FE59 + MCUmgr/SMP), with MCUboot image-slot model and S140 SoftDevice split.
  - Evidence:
    - `softdevice.bin` and `bootloader.bin` disassembly/offset analysis places softdevice at `0x00001000` and bootloader at `0x000F8000`.
    - `sd_req [0x0100,0x0102]` in init packet bytes.
    - FE59/SMP UUIDs in capture/runtime docs.
  - Interpretation: **This is explicitly consistent with an S140-style Nordic stack placement on a 1MB-class Nordic layout, and nRF52840 is currently the best match.** Caveat: this remains an inference from memory-map/layout evidence, not a direct on-disk part-ID field.
  - Confidence: **High** for S140-class Nordic stack layout; **Medium** for exact SoC SKU/SDK revision.

## Inference-level notes

- The R1 SoC inference currently points to nRF5x generation from artifact semantics and DFU service contracts, but there is still no direct silicon-unique constant proving the exact model number.
- The case MCU is confirmed as STM32L0 series via GPIO base address (0x50000000). Exact part number (L071/L081) remains inferred from dual-bank flash capability.

## Practical recommendations by task

- For **G2 main firmware work**, start from:
  - IAR-embedded Apollo510b conventions,
  - Ambiq HAL / drivers inferred by symbol paths,
  - and FreeRTOS/Cordio/littlefs submodules in recovered source tree.
- For **R1 ring DFU tooling and validation**, use Nordic secure-DFU + MCUboot flow assumptions and validate `B210_*` bundle behavior.
- For **Case MCU**, STM32CubeL0 HAL is confirmed. All major subsystems symbolized (UART, I2C, Flash, GPIO, Timer, FreeRTOS). 410/414 functions at HIGH confidence.
