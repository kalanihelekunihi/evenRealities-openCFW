# Infineon PSoC 4000T CY8C4046FNI

**Used in:** G2 glasses, per temple, as the touch-strip and proximity (wear)
controller. Tags: [vocabulary](../README.md#confidence-vocabulary).

## Identification

| Evidence | Tag |
|---|---|
| Apollo driver `drv_cy8c4046fni`; touch payload is Cortex-M0+ code using CapSense MSCLP (5th-gen) and PSoC 4 peripheral bases | FW High (`g2/components/apollo_main/core_overlay/drv_cy8c4046fni.c:173-200`; `g2/docs/research/g2-touch-identity-recovery.md:15,43`) |

## Documents

| Document | URL |
|---|---|
| Part page CY8C4046FNI-T452T | https://www.infineon.com/part/CY8C4046FNI-T452T |
| Part page CY8C4046FNI-T412T | https://www.infineon.com/part/CY8C4046FNI-T412T |
| Family page | https://www.infineon.com/products/microcontroller/32-bit-psoc-arm-cortex/psoc-4-mcu/4000/4000t |
| Datasheet hub | https://documentation.infineon.com/psoc4000t/docs/klf1738900617592 |
| Datasheet v09 (distributor copy) | https://www.mouser.com/pdfDocs/Infineon-PSoC_4000T_MCU_datasheet-DataSheet-v09_00-EN.pdf |

## Key specifications (DS)

| Item | Value |
|---|---|
| Core | Arm Cortex-M0+, up to 48 MHz |
| Memory | 64 KB flash, 8 KB SRAM |
| Sensing | Multi-Sense: 5th-gen CAPSENSE (MSCLP), inductive, liquid level, hover |
| Package | "FNI" = WLCSP |

## G2 use (FW)

| Item | Value |
|---|---|
| Host link | I2C slave on SCB1 (`0x40250000`, IRQ 7), 7-bit address 0x0C on Apollo "I2C bus 5" |
| Attention | PRT4 pin 0, active-low (DR_CLR `0x40040444`, DR_SET `0x40040440`) |
| CapSense block | MSCLP0 at `0x40290000` |
| Firmware | `firmware/touch.bin` v2.2.0.1, GCC/newlib, polled super-loop, EEPROM emulation (`UNVE` magic); flash image `[0,0x867C)`, SP `0x20002000`, reset `0x4675`; resident DFU engine at ≥`0x8680` not shipped |
| Protocol | See [g2-glasses.md](../g2-glasses.md#4-inter-processor-links) |

## Register map / SVD

PSoC 4 register TRMs and PDL headers come with ModusToolbox (Infineon);
the SVD for the PSoC 4000T ships in the Infineon device support packages.
No URL for the SVD itself was opened for this page.

## Relevance to decompilation

Load at `0x00000000` (flash) with SRAM `0x20000000–0x20001FFF`; label SCB1,
GPIO PRT2/3/4 and MSCLP0 at the bases above.
