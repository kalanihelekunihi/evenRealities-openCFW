# Independent review 2209

**Result:** PASS_SCOPED.

The source, body [0x60EA, 0x6140) and all receipt files match their declared hashes. Independent Thumb/M-class disassembly agrees with the candidate listing.

An isolated replay regenerated all 48 fixtures exactly. Original 60EA, 5FC6 and the port configuration leaves execute without interception. Count 0/1/3 and mode, enable and PRIMASK combinations verify child tuples including stack enable, ordered unconditional writes to port+68, all four resulting port words, R4/R8–R11, SP and mask restoration.

The decoded code loads entries from context+24, reloads root and the byte count at root+44 for the loop test, calls 5FC6 with port/pin/function/mode and the fifth stack argument, then stores `1 << pin` at port+68 before advancing by eight bytes.

**Limits:** Count and pointers are static in the fixtures. Invalid-pin BKPT continuation, pointer mutation, physical port effects, aliasing and concurrency remain unverified. No canonical admission is made.
