# Fixed IOM power preparation

`power_prepare.c` reconstructs the stock operation2 prefix only. `opencfw_iom_powerdown_prepare` returns0 for preparation,2 for invalid handle,3 for enabled/busy state. `opencfw_iom_disable_then_prepare` ignores the disable status before preparing, matching the bounded release ordering. Neither API powers down hardware or proves shutdown safety.

Build `make -C g2 radio-iom-power-prepare-simulator`; run `verify.py --elf <ELF> --output <new JSON>` using the installed Unicorn environment. The output must be fresh; previous evidence remains preserved. [Report and evidence](../../../analysis/radio-iom-power-prepare-2026-10-05/REPORT.md) describe the13-register retention layout, descriptor aliasing and prepared-only boundary.

These are reconstructed MIT-licensed consumer bodies, not attributed SDK originals. Existing Ambiq CMDQ/PRIMASK source is reused unchanged with its BSD-3-Clause notices. The isolated Cortex-M4 O2 semantic profile is not a stock link map, production binary or byte-identical firmware. The inherited masked intermediate RAM-store difference and missing resident-ROM timing provider remain explicit limits.
