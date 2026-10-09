# mtb-pdl-cat2 peripheral driver library v2.0.0

See the [README.md](./README.md) and the
[PDL API reference manual](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/index.html)
for a complete description of the Peripheral driver library.

## What's included?

### New Features

Support for a new device of the USB PD device series:
- CCG8

Removed startup files. Now it is a part of the BSP package.

### Updated personalities

All the legacy (non-latest) personality versions are removed.

- SCB 1.0 - Personality updated to do not show empty connection options.
- Pin 2.0 - Deleted Input Buffer Mode, because this mode isn't in the current devices.
- CSD 2.0 - Improved pin assignment functionality.
- ILO 2.0 - The CY_CFG_SYSCLK_ILO_ENABLED generation is removed as not needed anymore.
- HFCLK 3.0 - The maximum output frequency check is added for devices with system clock frequency limitation.
- PLL 2.0 - The DRC which required to upgrade the HFCLK version to latest is removed (because there are no non-latest versions).
- PUMPCLK 2.0 - The personality became unavailable for devices which do not have any pump clock consumers.
- SYSCLOCK 2.0 - The Cy_SysClk_IloDisable()() is called in case when the ILO resource is not enabled.
- WCO 2.0 - The personality became unavailable for devices which do not have WCO-GPIO connections.
- WDT 2.0 - The Cy_WDT_Enable() call is removed from the generated code to eliminate unexpected WDT reset. User should explicitly call the Cy_WDT_Enable() in the application code.
- LPComp 1.0 - The new parameter 'Trigger Output' is added.

**Note** that most personality revisions are major, so the backward incompatible changes are possible.

### Updated drivers

- [GPIO 3.0](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__gpio.html)

- [SysClk (System Clock) 3.0](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__sysclk.html)

- [SysLib 3.0](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__syslib.html)

- [CryptoLite 1.10](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__cryptolite.html)

- [USBFS 2.0](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__usbfs__dev__drv.html)

- [USBPD (USB Power Delivery) 2.0](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__usbpd.html)

- [SCB 4.20](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__scb.html)

- [SAR 2.30](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__sar.html)

- [DMAC 1.20](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__dmac.html)

- [I2S 1.10](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__i2s.html)

**Note-1:** Most driver revisions are major, so the backward incompatible API changes are possible.
In case of ModusToolbox&trade; usage regenerate the generated source files with Device Configurator (and other configurators if any used).

**Note-2:** In scope of DMAC v1.20, updated the Cy_DMAC_Descriptor_SetDstAddress() function interface. A compilation warning/error may display about the discarded ‘const’ qualifier in CAPSENSE™ middleware v3.0.0. The problem is applicable only for the fifth-generation CAPSENSE™ devices under CS-DMA scan mode. You can ignore that as it causes no functional issues.

The compilation warning will be reported if the GCC_ARM or ARM compiler is used with default options.  
The compilation error will be reported if the IAR compiler is used with the default options.

To compile the project using the IAR compiler with the Eclipse IDE for ModusToolbox™, update the CFLAGS section of the project Makefile with the --diag_warning=Pe167 option (CFLAGS+=--diag_warning=Pe167).  
To compile the project using the IAR Embedded Workbench IDE, do the following:  
1.	Right-click the capsense node in the Workspace explorer and select *Options* from the context menu.
2.	Select the C/C++ Compiler category and switch to the Diagnostics tab.
3.	Check the Override Inherited Settings CheckBox.
4.	Update the Treat as Warning EditBox with the Pe167 option.



### Drivers with patch-version updates

- [CSD 1.10.2](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__csd.html)

- [MSC 1.10.2](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__msc.html)

## Defect fixes

See the Changelog section of each driver in [PDL API reference](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/modules.html) for all fixes and updates.

## Supported software and tools

This version of PDL was validated for compatibility with the following software and tools:

| Software and tools                                                            | Version      |
| :---                                                                          | :----        |
| ModusToolbox&trade;                                                           |  3.0.0       |
| [core library](https://github.com/Infineon/core-lib)                          |  1.3.1       |
| [device-db](https://github.com/Infineon/device-db)                            |  4.0.2       |
| CMSIS-Core(M)                                                                 |  5.8.0       |
| GCC compiler                                                                  | 10.3.1       |
| IAR compiler                                                                  |  9.30.1      |
| Arm&reg; compiler 6                                                           |  6.16        |

## More information

- [Peripheral driver library README.md](./README.md)

- [Peripheral driver library API reference manual](https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/index.html)

- [ModusToolbox&trade; Software Environment, Quick Start Guide, Documentation, and Videos](https://www.infineon.com/cms/en/design-support/tools/sdk/modustoolbox-software)

- [ModusToolbox&trade; Device Configurator Tool Guide](https://documentation.infineon.com/html/modustoolbox-software/en/latest/tool-guide/ModusToolbox_Device_Configurator_Guide.html)

- [AN79953 - Getting started with PSoC&trade; 4](https://www.cypress.com/an79953)

- [PSoC&trade; 4 technical reference manuals](https://www.cypress.com/search/all?f%5B0%5D=meta_type%3Atechnical_documents&f%5B1%5D=resource_meta_type%3A583&f%5B2%5D=field_related_products%3A1314)

- [PSoC&trade; 4 datasheets](https://www.cypress.com/search/all?f%5B0%5D=meta_type%3Atechnical_documents&f%5B1%5D=field_related_products%3A1297&f%5B2%5D=resource_meta_type%3A575)

- [PMG1 device family](http://www.cypress.com/PMG1)

---
© 2020-2022, Cypress Semiconductor Corporation (an Infineon company) or an affiliate of Cypress Semiconductor Corporation.
