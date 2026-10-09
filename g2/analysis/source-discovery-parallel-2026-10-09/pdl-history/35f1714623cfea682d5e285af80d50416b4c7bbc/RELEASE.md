# mtb-pdl-cat2 peripheral driver library v2.21.0

See the [README.md](./README.md) and the
[PDL API reference manual](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/index.html)
for a complete description of the Peripheral driver library.

## What's included?

### New Features
- Added support for PMG1-B2 device family.
- Updated the SysClk driver to support Dynamic IMO on PSOC&trade; 4100S Plus device.
- Updated the SAR driver to support Dynamic IMO on PSOC&trade; 4100S Plus device.
- New Dock configuration table features added to support PMG1S3 Dock SDK 1.3
- Added support for CCGx_CFP Dual port dock part numbers to enable dual port configuration functionality in USBPD implementation.
- Added new MPNs for PSOC&trade; 4100S Plus device families.

### Updated drivers
- [SysClk 3.70](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__sysclk.html)
- [SAR 2.90](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__sar.html)

### New drivers

### Updated personalities
* Updated Personalities (in 10.0 folder):
  * peripheral:
    * wdc-1.0.cypersonality
  * platform:
    * crwdt-1.0.cypersonality 


## Defect fixes

See the Changelog section of each driver in [PDL API reference](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/modules.html) for all fixes and updates.

## Supported software and tools

This version of PDL was validated for compatibility with the following software and tools:

| Software and tools                                                            | Version      |
| :---                                                                          | :----        |
| ModusToolbox&trade;                                                           |  3.7.0       |
| [Infineon Core Library](https://github.com/Infineon/core-lib)                 |  1.7.0       |
| [Device Database](https://github.com/Infineon/device-db)                      |  4.36.0      |
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
