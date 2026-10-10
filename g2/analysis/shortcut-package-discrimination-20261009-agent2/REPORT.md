# Authenticated package/body discrimination

2026-10-09. Private P2 comparator only. Active workflow README and all three integrated shortcut reports, release archaeology, and vendor-history reports were read. No firmware implementation, canonical coverage, gate, authenticated input, or submodule registration changed.

## New Apollo exclusion and reset-coordinate correction

`probe.py` authenticates all six payloads against `g2/workflow/target.json`, verifies the earlier analysis ELF contains the exact main payload, and records original bounded-body hashes. The actual reset vector is **0x005E4233**, meaning Thumb entry **0x005E4232**, rather than 0x005E4294. The latter is a downstream runtime entry, despite the consolidated memory-map wording. This is a comparator correction, not a canonical edit.

The actual entry sets MSPLIM and PSPLIM to 0x2007D000 and calls 0x005E4254. That helper creates a two-word stack seal with 0xFEF5EDA5, sets PSP, calls 0x005E4270 and then the runtime entry 0x005E4294. The bounded FPU helper at 0x005E4270 enables CP10/CP11 through CPACR, emits DSB/ISB and sets FPSCR=0x02040000. Runtime callback 0x005E4228 writes VTOR=0x00438000 and returns 1, causing the relative initializer table at 0x005E42B4 to execute before the later startup calls.

This ordered chain excludes direct reuse of the acquired Apollo_DFP 1.5.2 Reset_Handler plus SystemInit source pair. The pack reset explicitly powers all SSRAM blocks before calling SystemInit; the authenticated entry/helper chain has no SSRAM power operation in that position. The supplied SystemInit unconditionally enables SCB CCR loop/branch cache and writes SystemCoreClock, with optional FPU/PDEPU operations. The bounded stock FPU helper instead explicitly writes FPSCR and has neither the unconditional CCR cache write nor the SystemCoreClock store. It is therefore not that SystemInit body. Shared CPACR bits alone are insufficient source identity.

This exclusion applies to the supplied pair and bounded entry ordering. It does not prove that no later stock initializer configures SSRAM, cache, or clocks, and does not exclude edited Ambiq source elsewhere. The pack startup remains entirely disabled by `#if 0`; comparison uses its textual example, not a compiled producing object. The evidence supports an IAR runtime chain already independently identified by retained IAR project paths and scatter-table structure; it does not identify an exact IAR release or recover DLIB source.

## Remaining producing-family comparators

The STM32 source family is already registered. The prior concrete v1.6.3 MDK Timers recipe selects ArmCC 5.06/RVDS CM0 and is excluded by the stock Arm Compiler6 plus GCC-port evidence. CMSIS register names and leaf-body equality cannot discriminate another producing compiler recipe. No authenticated release-specific HAL body discriminator newly emerged here, so downloading historical DFPs would duplicate that source-family evidence.

The Infineon CAT2 DFP's dummy startup is already excluded as a producing source. The registered 4000T demo's Configurator schema and stock LP raw-IIR difference exclude direct demo reuse. Target .cycapsense inputs, generator version and dependency pin remain missing. The DFP supplies no additional generated table provider; another generic package adds no target identity.

The Ambiq SDK history already inspected alpha2-to-alpha3 transport code, and retained IAR-visible source paths establish a modified producing project family. No new authenticated version-specific startup or system body match justifies another Git source. The official pack source is an archive member already acquired, with hashes retained in this pass's receipt; no new download or proposed submodule is warranted.

GNU original-byte decoding materially resolves the comparison. Ghidra's existing decompilation was used only to locate the bounded candidate; it merges runtime code misleadingly at 0x005E4294 and misses the FPSCR side effect in 0x005E4270. Another Ghidra-MCP session, Ablation profile or REA orchestration pass would add no independent oracle for these straight-line register/call discriminators.

## Evidence and finite boundary

`receipt.json` binds all payloads, reset-vector words, six bounded body hashes and both official pack member hashes. `startup-gnu.txt` records independent instruction evidence; literal pool bytes in the linear listing are data, not claimed instructions. `probe.py` is replayable and writes only this owned directory.

The supplied package/source-family branch is exhausted for these authenticated discriminators. A target-specific source/configuration archive, actual matching compiler runtime package, or another authenticated body with release-specific behavior can reopen it. Whole-artifact P2 recovery and independent review remain open. No cybersecurity rejection occurred.
