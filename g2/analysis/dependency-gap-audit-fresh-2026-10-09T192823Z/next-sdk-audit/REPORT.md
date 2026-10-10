# New SDK variant/source candidate audit

Read-only ZIP/ar/ELF parsing on authenticated user-supplied5.2package; no duplicate extraction, SDK/firmware execution, redistribution, source/pin/index/Git/device changes. VARIANTS.json records six archives, two selected members per archive, compiler markers, ELF flags, executable/symbol/relocation/ABI-metadata hashes. Retained metadata is not binary source coverage.

## Archive-family constraints and eliminated duplicate

All six archive hashes match the emulator's recorded inventory: standard/Lite GCC, IAR and Keil6. Selected IAR cmdlist/blender members are ET_REL ARM machine40, flags05000000 and contain IAR9.70.1.475/W64 producer strings. Selected GCC members explicitly record GNU13.2.1 Cortex-M55 Thumb/hard-float/armv8.1-m/main+FP+MVE/-O3 options. Keil selected members have no marker matching the narrow scanned string patterns; this is not absence of compiler metadata or proof of incompatibility. Raw ELF flags alone do not certify floating-point calling ABI or all architecture attributes.

Apollo510 versus Apollo510L IAR selected command-list/blender objects have differing overall member hashes but identical executable .text, .rel.text, .symtab, .strtab, .ARM.attributes and .iar.rtmodel bytes. Thus selected relocation records and their symbol definitions/strings are also identical, not just code text. No new text/linkage discriminator is gained by rerunning the closed sectored-function test with Lite. Differences in whole-object/debug bytes are not a different executable implementation. Scope is these two members only; no whole-archive deduplication or general Lite hardware compatibility follows.

The closed230stock/222candidate sectored result remains specific. Different compiler-family variants cannot be excluded merely because the selected IAR member differs. A new named stock extent plus explicit symbol/relocation closure is prerequisite to another command producer comparison. No verified such new function was selected here; avoid arbitrary all-member byte scanning and version/flags sweeps.

## Concrete new source lead outside graphics

In-memory comparison of ZIP Apollo510 am_hal_mspi.c with canonical local am_hal_mspi.c yields only three notice/release-label hunks. No new functional MSPI discriminator exists in those inspected files; another source download would duplicate it.

Apollo510 am_hal_iom.c has27diff hunks and actual implementation changes. One clean finite differential is new AM_HAL_IOM_MI2CCFG_STRDIS_DEFAULT=1, used in three I2C clock setup branches at SDK lines3696,3716,3736. Canonical5.1source lacked those STRDIS additions. Both source identities and full hunk coordinates are in HAL-SOURCE-DIFFERENCES.json. This is new source evidence, so a carefully bound follow-up would not repeat an old IOM probe without new information.

Next finite verification: authenticate a locked IOM I2C clock-configuration function/branches, exact extent/hash and register header mapping; compare its three MI2CCFG writes against old/new constant equations with STRDIS bit explicitly decoded from the correct Apollo510 header. Static constants could discriminate an unchanged5.1versus5.2software branch. They cannot identify the entire SDK revision, private patches, live IOM routing, clock-stretch behavior or producer toolchain. No bound stock extent was found in the inspected symbol/JSON/report names, so this remains a candidate pending target binding rather than an execution-ready assignment. Owner/discovery should coordinate that target before implementation or tests.

No useful inference follows from API/version naming alone. New headers/source can still reveal bounded changed providers even though proprietary implementation source, exact producer configuration and physical inputs remain unavailable. Therefore neither this variant inventory nor earlier closed DSP/LZ4/Nema results support global source exhaustion. Stop this pass at selected metadata deduplication and the specifically identified IOM source delta; review new owner/discovery evidence when supplied.
