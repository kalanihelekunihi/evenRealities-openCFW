# Independent review 2207

**Result:** PASS_SCOPED.

The source, body [0x6078, 0x60EA) and all receipt files match their declared hashes. Independent Thumb/M-class disassembly agrees with the stored listing.

An isolated replay regenerated all 96 fixtures exactly. It covers count 0/1/3, both direction, mode, enable and PRIMASK values, and alternating pin 0/7 and port choices. Assertions verify each 5FC6 tuple including its fifth stack argument, ordered port+64/+68 writes, all four resulting configuration words per port, R4/R8–R11, SP and PRIMASK.

The decoded loop gets the entry pointer from context+20, reloads the context root and halfword count, compares the index and count unsigned, and calls 5FC6 with the entry port/pin, saved function/mode and stack enable. It then writes one pin bit to the direction-selected register and advances the entry by eight bytes.

**Limits:** Count and pointers are static in these fixtures; dynamic mutation/reload behavior is not tested. Invalid-pin BKPT continuation, physical register effects, aliasing and concurrency remain unresolved. No canonical admission is made.
