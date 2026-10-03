# Independent review 2645: profile apply routing

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate, source, body, and artifact hashes match. Independent objdump decoding confirms the branch structure and saved-register epilogue in `[0x42A4BC,0x42A546)`. The table pointer literal resolves to `0x20000098`. I reran a copy of the emulator into a fresh isolated directory; all 256 fixtures pass using synthetic table entries at indices 0 and 26.

The fixtures confirm branch-specific child ordering and arguments, the mixed-low-bit value, the route helper’s stack-byte output pointer, and the conditional indirect call. A nonzero route return skips dispatch; zero dispatches through the synthetic target. The epilogue returns the saved newsecond word with its low byte replaced by 26 or the route-written index, and returns saved oldsecond in R1, with R4-R8 and SP preserved.

Children, indirect destinations, and table contents are controlled or synthetic; their real semantics and ownership are not established. Bounds, concurrency, aliasing, and physical effects remain unresolved. This private evidence is not canonical admission.
