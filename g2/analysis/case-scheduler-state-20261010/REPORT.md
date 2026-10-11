# CASE scheduler state candidate

**COMPLETE bounded source candidate:** original `0x0800ca4c..0x0800ca66` (26 code bytes) reads scheduler words at base `0x20000128`, offsets `0x14` and `0x30`. The authenticated literal at `0x0800ca68` confirms the base address. `scheduler_state.c` returns 1 before scheduler activation, 2 when active and not suspended, or 0 while suspended.

The Cortex-M0+ candidate compiles. `verify.py` checks the wrapped and raw CASE hashes and compares original/source execution for nine combinations of the two 32-bit words, including zero, one and all-ones. All nine return, RAM and stack comparisons pass. `results.json` records exact compiler/source/ELF/firmware identities.

The CASE archive now has 16 objects, 34 provided global symbols and 20 unresolved names. Scheduler state writers, task transitions, memory initialization, full linking and image byte equality remain unverified. At least 20 provider contracts plus integration phases remain; full-image effort cannot be estimated from this wrapper.
