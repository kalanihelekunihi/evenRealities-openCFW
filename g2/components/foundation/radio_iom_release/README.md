# Local IOM-like release consumer

See [pseudocode/ownership](../../../analysis/radio-iom-release-2026-10-05/pseudocode.md). Consumer bodies are reconstructed, not SDK-attributed. Existing pinned Ambiq CMDQ and PRIMASK providers are reused unchanged, with original BSD-3-Clause notices.

Build `make -C g2 radio-iom-release-simulator`; verify.py accepts `--elf <ELF> --output <fresh JSON>`. Synchronous semantic profile only. Raw original/source index-store sequences differ on wrap and are explicitly tested/disclosed; no free/drain/callback/NVIC/hardware-shutdown or production byte-match claim.
