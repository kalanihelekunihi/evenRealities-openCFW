# mtb-pdl-cat2 peripheral driver library v2.20.0

See the [README.md](./README.md) and the
[PDL API reference manual](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/index.html)
for a complete description of the Peripheral driver library.

## What's included?

### New Features
- Added support for new PSOC&trade; 4 HVPA SPM 1.0 device family.
- Added new drivers for the PSOC&trade; 4 HVPA SPM 1.0 devices.
Please refer to the [New drivers](#new-drivers) section below for details.
- Updated the CANFD driver to incorporate PSOC&trade; 4 HVPA SPM 1.0 platform configuration.
- Updated the Crypto driver with improved error handling in Cy_Crypto_Sha_Partial function.
- Updated the SysFault driver to incorporate PSOC&trade; 4 HVPA SPM 1.0 platform support.
- Updated the SysClk driver to incorporate PSOC&trade; 4 HVPA SPM 1.0 platform configuration.
- Updated the SAR driver with enhanced EXPMUX functionality.
- Updated the DSADC driver with OCD feature support for PSOC&trade; 4 HVPA SPM 1.0 devices.
- Updated the CTB driver with new function for PSOC&trade; 4 devices.

### Updated drivers
- [CANFD 1.30](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__canfd.html)
- [Crypto 1.10](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__crypto.html)
- [SysFault 1.20](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__sysfault.html)
- [SysClk 3.60](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__sysclk.html)
- [SAR 2.80](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__sar.html)
- [DSADC 1.10](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__dsadc.html)
- [CTB 1.10](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__ctb.html)

### New drivers
- [ISOUART 1.0](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__isouart.html)

### Updated personalities
- The SAR personality for PSOC&trade; 4 HVMS Platform improved to clarify functionality of "Boost Pump" field.
- The ILO clock diagram for PSOC™ 4 HVMS/PA Platform improved to display accurate clock tolerance specification.
- Enabled multiple personalities on PSOC&trade; 4 HVPA SPM 1.0 device family: SysClocks, ECO, DSADC, CANFD, LIN.
- Added new personalities for PSOC&trade; 4 HVPA SPM 1.0 device family: ISOUART, OCD.
- The sysanalog personality for PSOC&trade; 4 Platform improved to choose clock source of the Pump.

## Defect fixes

See the Changelog section of each driver in [PDL API reference](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/modules.html) for all fixes and updates.

## Supported software and tools

This version of PDL was validated for compatibility with the following software and tools:

| Software and tools                                                            | Version      |
| :---                                                                          | :----        |
| ModusToolbox&trade;                                                           |  3.7.0       |
| [Infineon Core Library](https://github.com/Infineon/core-lib)                 |  1.7.0       |
| [Device Database](https://github.com/Infineon/device-db)                      |  4.35.0      |
| CMSIS-Core(M)                                                                 |  6.1.0       |
| GCC compiler                                                                  |  14.2.1      |
| IAR compiler                                                                  |  9.50.2      |
| Arm&reg; compiler 6                                                           |  6.22.0      |

## More information

- [Peripheral driver library README.md](./README.md)

- [Peripheral driver library API reference manual](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/index.html)

- [ModusToolbox&trade; Software Environment, Quick Start Guide, Documentation, and Videos](https://www.infineon.com/cms/en/design-support/tools/sdk/modustoolbox-software)

- [ModusToolbox&trade; Device Configurator Tool Guide](https://documentation.infineon.com/html/modustoolbox-software/en/latest/tool-guide/ModusToolbox_Device_Configurator_User_Guide.html)

- [AN79953 - Getting started with PSOC&trade; 4](https://www.infineon.com/dgdl/Infineon-AN79953_Getting_Started_with_PSoC_4-ApplicationNotes-v21_00-EN.pdf?fileId=8ac78c8c7cdc391c017d07271fd64bc1&utm_source=cypress&utm_medium=referral&utm_campaign=202110_globe_en_all_integration-an_vanitylink)

- [PSOC&trade; 4 technical reference manuals](https://documentation.infineon.com/psoc4/docs/hup1702048028817)

- [PSOC&trade; 4 datasheets](https://documentation.infineon.com/psoc4/docs/qqs1702048028479)

- [PMG1 device family](https://www.infineon.com/cms/en/product/universal-serial-bus-usb-power-delivery-controller/usb-c-and-power-delivery/ez-pd-pmg1-portfolio-high-voltage-mcus-usb-c-power-delivery/?utm_source=cypress&utm_medium=referral&utm_campaign=202110_globe_en_all_integration-product_families)

- [CCGxF_CFP device family](https://www.infineon.com/products/universal-serial-bus/usb-c-power-delivery-controllers)

---
© Infineon Technologies AG or an affiliate of Infineon Technologies AG, 2020-2026.
