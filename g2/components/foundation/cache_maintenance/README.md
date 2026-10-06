# DMA cache maintenance

Reconstructed stock register/barrier contract with two-word range descriptor. `opencfw_cache_clean` cleans; `opencfw_cache_invalidate` selects invalidate-only or clean-and-invalidate using the low flag byte. NULL selects whole cache. Both return0; that is not a hardware-coherency result.

Build `make -C g2 cache-maintenance-simulator`. Run `verify.py --elf <ELF> --output <fresh JSON>` with the installed Unicorn environment. [Analysis and evidence](../../../analysis/cache-maintenance-2026-10-06/REPORT.md) cover384 stock bytes and the actual display/audio call sites. The source is a bounded MIT reconstruction, not SDK-attributed code or a production firmware link map.

Caller must supply mapped, aligned descriptor words when the cache is enabled. Signed nonpositive lengths skip maintenance; the stock loops use32-byte steps and do not mask interrupts. Physical cache-line effects, partial-line ownership and DMA visibility remain outside the register-only comparison.
