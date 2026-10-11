# CASE ISR deferred clear wrapper

**COMPLETE bounded wrapper:** `xEventGroupClearBitsFromISR` occupies original `0x0800c478..0x0800c48c` (20 bytes including its callback literal). It forwards the authenticated `vEventGroupClearBitsCallback` pointer, event group, bit mask and null wake pointer to `xTimerPendFunctionCallFromISR`, returning that child's result.

The Cortex-M0+ source compiles. `verify.py` checks the CASE image hashes and exact callback literal `0x0800bf85`, then executes original and source wrapper for 24 combinations of event handle, bit mask and lower result. Ordered callback identity/arguments, return and SP agree in every case. Both lower bodies are explicit call boundaries; `results.json` records source/compiler/ELF/original identities.

The CASE source archive has 21 objects and 40 provided global names. It has 16 unresolved names because closing this direct wrapper exposes its two lower providers. The timer command queue, deferred callback, event ownership/lifetime, actual ISR timing and whole-payload byte equality remain open. At least 16 distinct provider decisions plus integration phases remain; image-wide effort cannot be estimated from this wrapper.
