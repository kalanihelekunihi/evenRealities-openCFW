# Firmware Bundles and Hardware Targets

This document maps the locally recovered firmware bundles to their hardware targets and records how each bundle matters to `openCFW`.

## Confirmed Bundle Inventory

| Bundle | Target | Wrapper / Format | Status | openCFW Relevance |
|---|---|---|---|---|
| `ota_s200_firmware_ota.bin` | G2 left/right main runtime | 32-byte preamble + ARM image | Confirmed | Primary custom-firmware target |
| `ota_s200_bootloader.bin` | G2 Apollo510b bootloader | Raw ARM vector table | Confirmed | Needed for boot/handoff understanding |
| `firmware_ble_em9305.bin` | EM9305 BLE radio patch | Segmented patch header | Confirmed | Secondary target; radio patch semantics still partial |
| `firmware_codec.bin` | GX8002B audio codec MCU | FWPK | Confirmed | Audio/control bridge target |
| `firmware_touch.bin` | CY8C4046FNI touch MCU | FWPK + CRC32C | Confirmed | Touch/proximity integration target |
| `firmware_box.bin` | G2 charging case MCU | EVEN wrapper + checksum | Confirmed | Case relay / OTA relay target |
| `B210_ALWAY_BL_DFU_NO` | R1 Nordic failsafe bootloader | Nordic Secure DFU package | Confirmed | Ring-side failsafe boot artifact; not the standalone ring app runtime |
| `B210_BL_DFU_NO_v2.0.3.0004` | R1 Nordic versioned bootloader | Nordic Secure DFU package | Confirmed | Ring-side boot artifact with instruction-anchored startup path |
| `B210_SD_ONLY_NO_v2.0.3.0004` | R1 Nordic SoftDevice | Nordic Secure DFU package | Confirmed | Ring-side BLE-stack artifact with instruction-anchored idle/reset path |
| Standalone R1 application runtime image | R1 ring main runtime | Not yet isolated in corpus | Missing | Clean-room ring-firmware implementation remains blocked until the app image exists |
| R1 charger firmware | Charging cradle | None | Confirmed absent | No custom firmware target |

## Confirmed Hardware Platform Map

| Device / IC | Status | Notes |
|---|---|---|
| Apollo510b | Confirmed | Main G2 SoC for `ota_s200_firmware_ota.bin` |
| JBD4010 / A6N-G | Confirmed | uLED display path, second-source panel evidence present |
| EM9305 | Confirmed | BLE radio patch component exists separately from the Apollo host |
| GX8002B | Confirmed | Audio codec MCU with TinyFrame host protocol |
| CY8C4046FNI | Confirmed | Touch controller with separate firmware payload |
| ICM-45608 | Confirmed | Main IMU |
| OPT3007 | Confirmed | ALS input for brightness sync |
| BQ25180 / BQ27427 / nPM1300 | Confirmed | Charging, fuel gauge, and PMIC path |
| MX25U25643G | Confirmed | External flash / LittleFS storage |
| Case MCU | Partial | STM32-like family, exact part still not closed |
| R1 ring SoC | Partial | Nordic nRF5x family; exact production SKU and standalone runtime image are still missing |

## Main Runtime Ownership

| Area | Owner | Confidence |
|---|---|---|
| UI, BLE host, scheduler, files, OTA orchestration | Apollo510b main firmware | Confirmed |
| Radio firmware / low-level BLE radio patching | EM9305 component firmware | Confirmed |
| Audio codec / wake-word path | GX8002B | Confirmed |
| Touch / proximity logic | CY8C4046FNI | Confirmed |
| Case battery / dock state / case OTA target | Case MCU via G2 relay | Confirmed |
| Ring gesture / ring health runtime | R1 firmware | Partial; protocol known, versioned/failsafe bootloader plus SoftDevice artifacts exist, standalone app runtime image still missing |

## Custom Firmware Target Priority

1. Apollo510b main runtime (`ota_s200_firmware_ota.bin`)
2. Apollo510b boot / update flow compatibility
3. EM9305 interaction boundary from the Apollo side
4. Touch / codec command bridges
5. Case relay path
6. R1 runtime replacement only after a standalone ring application runtime artifact is available; until then, limit ring work to protocol and Nordic-bundle compatibility

## Source Documents

- `../firmware/firmware-files.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/s200-firmware-ota.md`
- `../firmware/s200-bootloader.md`
- `../devices/g2-glasses.md`
- `../devices/g2-case.md`
- `../devices/r1-ring.md`
