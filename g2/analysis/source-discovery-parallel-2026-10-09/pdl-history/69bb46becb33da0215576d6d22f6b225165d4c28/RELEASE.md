# mtb-pdl-cat2 peripheral driver library v2.0.0 Beta1

See the [README.md](./README.md) and the
[PDL API reference manual](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/index.html)
for a complete description of the Peripheral driver library.

## What's included?

### New Features

Support for a new device of the PSoC 4 device series:
- PSoC 4000T

Note: Non-backward compatible interface changes were made in the sysclk and gpio drivers. For details, refer to the driver's changelog.

Removed startup files. Now it's a part of the BSP package.

### New personalities

- MSCLP

### Updated personalities

All the legacy (non-latest) personality versions are removed.

- SCB 1.0 - Personality updated to do not show empty connection options.
- Pin 2.0 - Deleted Input Buffer Mode, because this mode isn't in the current devices.
- CSD 1.2 - The 'Enable CSDADC' disappeared because the CSDADC functionality is not supported yet.
- ILO 2.0 - The CY_CFG_SYSCLK_ILO_ENABLED generation is removed as not needed anymore.
- HFCLK 3.0 - The maximum output frequency check is added for devices with system clock frequency limitation.
- PLL 2.0 - The DRC which required to upgrade the HFCLK version to latest is removed (because there are no non-latest versions).
- PUMPCLK 2.0 - The personality became unavailable for devices which do not have any pump clock consumers.
- SYSCLOCK 2.0 - The Cy_SysClk_IloDisable()() is called in case when the ILO resource is not enabled.
- WCO 2.0 - The personality became unavailable for devices which do not have WCO-GPIO connections.
- WDT 2.0 - The Cy_WDT_Enable() call is removed from the generated code to eliminate unexpected WDT reset. User should explicitly call the Cy_WDT_Enable() in the application code.

Note that most personality revisions are major, so the backward incompatible changes are possible.

### Added drivers

- [MSCLP 1.0](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__msclp.html)

### Updated drivers

- [GPIO 3.0](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__gpio.html)

- [SysClk (System Clock) 3.0](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__sysclk.html)

- [SYSLIB 3.0](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__syslib.html)

- [CryptoLite 1.10](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__cryptolite.html)

- [SCB 4.10](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__scb.html)

Note that most driver revisions are major, so the backward incompatible API changes are possible.
In case of ModusToolbox usage regenerate the generated source files with Device Configurator (and other configurators if any used).

### Drivers with patch-version updates

## Defect fixes

See the Changelog section of each driver in [PDL API reference](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/modules.html) for all fixes and updates.

## Supported software and tools

This version of PDL was validated for compatibility with the following software and tools:

| Software and tools                                                            | Version           |
| :---                                                                          | :----             |
| ModusToolbox&#8482;                                                           |  3.0.0            |
| [core library](https://github.com/Infineon/core-lib)                          |  1.2.0            |
| [device-db](https://github.com/Infineon/device-db)                            |  4.0.0.2381       |
| CMSIS-Core(M)                                                                 |  5.4.0            |
| GCC compiler                                                                  | 10.3.1            |
| IAR compiler                                                                  |  8.42.2           |
| Arm&reg; compiler 6                                                           |  6.13             |

## More information

- [Peripheral driver library README.md](./README.md)

- [Peripheral driver library API reference manual](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/index.html)

- [ModusToolbox&trade; software environment, Quick Start guide, documentation, and videos](https://www.cypress.com/products/modustoolbox-software-environment)

- [ModusToolbox&trade; Device Configurator guide](https://www.cypress.com/ModusToolboxDeviceConfig)

- [AN79953 - Getting started with PSoC&trade; 4](https://www.cypress.com/an79953)

- [PSoC&trade; 4 technical reference manuals](https://www.cypress.com/search/all?f%5B0%5D=meta_type%3Atechnical_documents&f%5B1%5D=resource_meta_type%3A583&f%5B2%5D=field_related_products%3A1314)

- [PSoC&trade; 4 datasheets](https://www.cypress.com/search/all?f%5B0%5D=meta_type%3Atechnical_documents&f%5B1%5D=field_related_products%3A1297&f%5B2%5D=resource_meta_type%3A575)

- [PMG1 device family](http://www.cypress.com/PMG1)

---
© 2020-2021, Cypress Semiconductor Corporation (an Infineon company) or an affiliate of Cypress Semiconductor Corporation.
