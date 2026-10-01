# Independent review 2197

**Result:** PASS_SCOPED.

The source and all receipt-bound files match their hashes. The independently sliced code [0x6AC0, 0x6BCA), literal pool [0x6BCC, 0x6BD4), and eight-entry table [0xB4FC, 0xB51C) match their declared SHA-256 values. Independent Thumb/M-class decoding matches the stored code listing.

An isolated replay regenerated all 5,632 fixtures exactly. It covers every saved-mode byte, eleven requested full-word values, and both controlled 8FD0 outcomes. Assertions check equality-before-clear, allowed saved modes, requested-mode dispatch, helper order/arguments including the 6078 stack argument, mode-2 descriptor/config effects, 8FD0 status handling, selected register writes, and R4/R8/SP preservation.

The decoded dispatcher compares the saved byte against full incoming R0 before clearing config byte 115. Saved modes 0–2 and 5–7 proceed; other saved bytes return 1. Accepted prior modes clear the flag before the requested-mode greater-than-7 test. The jump-table paths and mode-2 failure return 64 agree with the pseudocode. The successful mode-2 path writes register-base offsets 264 and 288 before storing the requested mode.

**Limits:** Children 6078, 60EA, 6044, 8FD0, 6A80, 685C and 68EC are controlled. RAM-backed register and parameter blocks do not establish physical MMIO or helper effects; aliasing, concurrency and caller closure remain unresolved. Context pointers are dereferenced before equality handling and there is no null guard. No canonical admission is made.
