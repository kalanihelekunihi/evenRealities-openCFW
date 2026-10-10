# Vendor history source boundary pass

2026-10-09. Read active workflow README, PROCEDURE, CONTRACTS, REPOSITORY and prior source-gap, case compiler recipe, EM timer comparison and touch LP closure reports. This pass only acquires reference material and evaluates source discriminators. No firmware implementation, canonical coverage or gate update occurred.

## Newly acquired Infineon configuration exemplar

Official `https://github.com/Infineon/mtb-example-psoc4-msclp-capsense-demo.git`, `release-v4.0.0`, exact commit `2944e6269b1f17771176275dec8e8649fc853309` is now pinned at `third-party/reference/infineon-msclp-demo`. This revision is an example configuration comparator, not identified G2 source.

`templates/TARGET_CY8CKIT-040T/config/design.cycapsense` has SHA-256 `0da82b17811eb9fc38e6cc093be06c98b07b142f0dee18c064a7244f010ce192`. Its header states Configurator 6.20.0.5091, formatVersion 2, ModusToolbox 3.2.0. It declares DEVICE_TYPE P4_MSCV3_LP and explicit general filter, clock, CDAC and resampling parameters. It has five widget definitions (wake-on-touch CSD low-power, button, touchpad, guard-loop and guard mutual-cap) and an explicit scan-order table. It ships configuration XML, not generated `cycfg_capsense.c`.

The Makefile specifies GCC_ARM. Its dependency file names capsense `latest-v5.X`, a moving alias rather than a historical exact library pin. Thus copying its tool/dependency setup would not reconstruct a producing environment. The pinned XML nevertheless gives a concrete vocabulary/schema for translating already recovered stock tables into Configurator concepts, and documents which application-specific inputs cannot be supplied by generic CapSense middleware alone. The stock all-four-LP-slot path reported in touch LP closure is not this example's widget set; exact target config remains absent. No target stock tables were newly decoded or fitted.

Official example history inspected: release-v1.0.0 `c71077ec…`, v2.0.0 `78ba4deb…`, v3.0.0 `fecab229…`, v3.0.1 `6d34683f…`, v4.0.0 `2944e626…`, v5.0.0 `9b311ece…`. Public v5 master points at that latter revision. The earlier selected v4 revision preserves the visible 6.20/3.2 schema for comparison; choosing it is not a G2 date/version attribution. Repository license is the Cypress/Infineon EULA, retained in clone; it is not represented as an MIT library.

## Case producing-recipe negative discriminator

Official STM32CubeG0 v1.6.3 points at `878a6fd8ad440c70ee32bc6d7ad526babb6e04f4`. Acquired the official NUCLEO-G0B1RE FreeRTOS Timers MDK project at `acquisitions/stm32cube-g0-v163/FreeRTOS_Timers.uvprojx`, SHA-256 `89ce07fc61cf6df80adc7f0dd299b9def60f41f07fef93e2b4a98818f9a7104e`.

Project lines 13–14 select Arm Compiler **5.06 update 6 build 750**, `uAC6=0`; include paths select `portable/RVDS/ARM_CM0`. Stock case evidence instead identifies Arm Compiler6/armlink and a GCC ARM_CM0 port. This concretely excludes that official example's project recipe as a direct producing-project shortcut; matching chip family, FreeRTOS and vendor HAL is insufficient. It does not exclude individual HAL source bodies or every other STM32 project. No compiler matrix was repeated. Download URL: `https://raw.githubusercontent.com/STMicroelectronics/STM32CubeG0/878a6fd8ad440c70ee32bc6d7ad526babb6e04f4/Projects/NUCLEO-G0B1RE/Applications/FreeRTOS/FreeRTOS_Timers/MDK-ARM/FreeRTOS_Timers.uvprojx`.

## Ambiq history discriminator

Official ambiqhal tags inspected: SDK5.2.alpha.0 `511d4ec7…`, alpha.1 `5dc59c5b…`, alpha.2 `c416a1ba…`, alpha.3 `7ad8c379…`; current ambiq-stable `1577f6e5…`. The exact GitHub comparison alpha.2→alpha.3 reports `utils/am_util_ble_em9305.c` changed by two lines, and its patch only updates the package revision comment from `release_sdk5_2_a_2-228a2539a` to `release_sdk5_2_a_3-80ffa398f`. That version hop provides no new EM9305 transport semantics in that file. Most changes concern Apollo510L, a different silicon source tree. No duplicate full SDK download was justified.

## NationalChip and EM boundaries

Live official NationalChip lvp_kws branch main remains `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`; official lvp_sed has only main `28439b899f395b546f578bfe459dc4226428f0f0`, its last commit is README update 2024-11-13; tags query is empty. lvp_sed is already named by consolidated boot-container evidence, so the same unchanged source is not a new acquisition. Current lvp_kws README links lvp_aiot/viva for GX8002D; these application-generation projects are not established GX8002B model/compiler inputs and were not treated as matching providers.

Official EM9305 product/datasheet searches still route SDK availability through EM Microelectronic/vendor developer resources; they reveal no public historical v4.2 source package. Existing v4.6 wrapper comparisons already document raw mismatches and source/relocation ambiguity. Neither a newer public datasheet nor an unchanged Ambiq transport helper supplies the proprietary v4.2 RTEF/PML/controller implementations. The acquisition boundary remains an authenticated historical SDK/provider package, with license/provenance and actual source, rather than repeated search or a guessed port.

## Finite completion boundary

This history pass closes the checked unchanged public branches/tags and excludes one plausible vendor producing-project shortcut. It adds a useful missing configuration-schema exemplar. It does not establish universal third-party knowledge exhaustion: stock table-to-schema comparison, target corpus review and proprietary source inputs remain separate tasks. No newly acquired material is promoted to exact target-source attribution or hardware proof.
