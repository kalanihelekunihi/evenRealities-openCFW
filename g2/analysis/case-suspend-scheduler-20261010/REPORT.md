# CASE scheduler suspension counter

**COMPLETE bounded source candidate:** original `0x0800c380..0x0800c38a` (10 code bytes) increments the 32-bit scheduler suspended word at base literal `0x20000128` plus offset `0x30`. `suspend_scheduler.c` preserves unsigned wrap and performs no interrupt-mask operation.

The Cortex-M0+ source compiles. `verify.py` rechecks CASE wrapped/raw hashes and the literal, then runs original and compiled source for ten fixtures crossing counter 0/1/2/maximum-1/maximum and incoming PRIMASK 0/1. Final counter, PRIMASK and SP agree in every case. `results.json` records exact source/compiler/ELF/original identities.

The CASE archive has 19 objects, 38 provided globals and 16 unresolved names. Scheduler resume/drain and task activation remain separate providers. At least 16 provider contracts plus linker, layout and physical validation phases remain; full-image time is unknown.
