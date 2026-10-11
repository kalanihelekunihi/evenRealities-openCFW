# CASE ISR event bits getter

**COMPLETE bounded source candidate:** `xEventGroupGetBitsFromISR` at original `0x0800c4cc..0x0800c4de` (18 code bytes). The C body enters via the two already byte-matched CASE PRIMASK helpers, reads the event group's first 32-bit word and restores the previous interrupt mask.

The source and both mask helpers compile and link for Cortex-M0+. `verify.py` checks original CASE SHA and runs original source paths for ten event-word and incoming PRIMASK combinations. All ten returned bits, unchanged event bytes, final PRIMASK and SP comparisons pass. The verifier executes real source mask helpers rather than stubbing them. `results.json` records source/compiler/ELF/original identities.

The CASE archive now has 20 objects, 39 provided global names and 15 unresolved names. Physical interrupt races, event-group lifetime, other clear/set APIs, linker placement and whole-payload byte equality remain open. At least 15 provider contracts plus integration phases remain; completion time is unknown.
