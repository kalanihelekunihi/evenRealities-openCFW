# CASE control providers

**COMPLETE bounded source candidate:** original wrappers at `0x08006b80..0x08006b98` and `0x08006b98..0x08006bb0` plus the shared register-write leaf at `0x08004e9e..0x08004eaa` are reconstructed in `control_providers.c`. Together they cover 60 original bytes. The authenticated CASE image has wrapped SHA `36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374` and raw SHA `773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677`.

The source compiles for Cortex-M0+. `verify.py` compares original and compiled execution in Unicorn for 24 cases across all three entries. It checks ordered MMIO writes, both register values and restored stack pointer. Wrapper A selects mask `0x40`, wrapper B `0x80`, and the helper writes to offset `0x18` when enabled or `0x28` when disabled at base `0x50000000`. `results.json` records the compiler/source/ELF/firmware hashes and case details.

The CASE source archive now has 13 objects, 30 global definitions and 24 unresolved provider names. These three bounded bodies are complete as source/behavior candidates; hardware peripheral effects, reset state, actual linker placement and whole-payload byte identity remain open. At least the 24 distinct provider contracts plus integration/validation phases remain; a full-image duration cannot be inferred.
