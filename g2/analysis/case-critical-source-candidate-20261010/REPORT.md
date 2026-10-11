# CASE task critical-section providers

**COMPLETE bounded returning behavior:** `case_enter_critical` at original `0x0800bffc..0x0800c010` and `case_exit_critical` at `0x0800c014..0x0800c02c`, 44 original code bytes total. Both use the authenticated nesting word `0x2000019c`. Enter disables IRQs, increments the word and executes DSB/ISB; valid exit decrements and enables IRQs when it reaches zero. Original zero-nesting exit disables IRQs and loops forever; the C candidate preserves nonreturning behavior, but that path is not an execution equivalence claim.

The source compiles Cortex-M0+. `verify.py` rechecks original CASE SHA and both address literals; 14 returning original/source comparisons pass across nesting 0/1/2/all-ones where admitted and incoming PRIMASK 0/1. It checks final nesting, PRIMASK and SP. `results.json` records compiler, source, ELF and original hashes. Interrupt timing, physical scheduling and the nonreturning zero-nesting trace are outside these comparisons.

The CASE archive now has 18 objects, 37 provided global symbols and 17 unresolved names. At least those 17 provider contracts plus integration phases remain; whole-image completion cannot be estimated from this bounded pass.
