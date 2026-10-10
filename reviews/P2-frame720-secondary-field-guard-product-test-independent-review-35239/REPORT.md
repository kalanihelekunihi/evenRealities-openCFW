# Independent review 35239 — frame720 secondary field guard and product test

Status: partial / unaccepted. No global gate credit.

I replayed the locked artifact slice `[0x51D790,0x51D7D0)` from the hash-pinned image, reassembled the 64 bytes as Thumb code, and confirmed the disassembly reassembles byte-for-byte. The slice contains 17 instructions, 3 direct branch edges, and 0 calls.

The first BPL at `0x51D790` inherits N from the preceding LSLS and branches to `0x51DB58` when N is clear. On fallthrough, R2 is freshly loaded through R4; S0 is freshly loaded at R2+344 and quiet-compared with zero. VMRS transfers the FP comparison flags, and BLS at `0x51D7A2` branches to `0x51DC00` for ordered less/equal, excluding unordered. The next fresh word at R2+296 is compared with 1; BNE also reaches `0x51DC00`.

The remaining path freshly loads S0 from R2+348, multiplies by the immediately current S22, freshly loads S1 from R2+352, and performs nonfused VMLS using S1 and S23. VABS clears the result sign bit. The literal load at `0x51D7C4` reads the word at `0x51D8A8` into S2; the final quiet compare is S0 versus S2, followed by VMRS. FP rounding, exceptions, unordered behavior, architectural register state and memory fault ordering remain in scope. No call-preservation or object-coherence assumption was made.
