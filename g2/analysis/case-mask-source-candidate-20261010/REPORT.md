# CASE interrupt-mask providers

**COMPLETE exact source-byte candidates:** `case_mask_save` at original `0x080000f4..0x080000fc` (8 bytes) and `case_mask_restore` at `0x080000fc..0x08000102` (6 bytes). Source in `mask_providers.c` uses explicit ARM MRS/CPSID/MSR inline assembly with a compiler memory barrier. `verify.py` rebuilds for Cortex-M0+ and compares each complete `.text` function section with authenticated original bytes. Both are byte-identical: 14/14 code bytes; `byte-proof.json` records hashes and exact bytes.

The CASE archive now has 15 source objects, 33 provided global names and 21 unresolved names. Exact body identity closes only these two helpers. Original callers' critical-section nesting and scheduler behavior, linker placement, physical interrupt timing and whole-payload equality remain open. At least 21 provider contracts plus integration phases remain; complete image effort is unknown.
