# CASE PendSV request provider

**COMPLETE bounded source candidate:** `case_yield_request` at original `0x0800c0a0..0x0800c0b2` (18 code bytes) writes `0x10000000` to SCB ICSR `0xe000ed04` and executes ARM DSB/ISB. The source returns the original R0 value; its one CASE caller's declaration was aligned to that return register and discards the value.

`verify.py` rechecks authenticated CASE hashes and the SCB base literal, compiles for Cortex-M0+ and executes original/source in Unicorn. Six combinations of incoming R0 and PRIMASK pass with equal ordered ICSR writes, return register, mask, SP and register-state bytes. `results.json` records source/compiler/ELF/firmware identities. Actual PendSV scheduling and device interrupt timing require hardware evidence.

The CASE archive now has 17 objects, 35 provided globals and 19 unresolved names. At least 19 provider contracts plus startup, linking and byte-equality phases remain; full-image effort is unknown.
