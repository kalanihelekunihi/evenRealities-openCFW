# Independent review 2595: transition index setter

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate's artifact and source hashes match. The original body `[0x42CEA4, 0x42CED8)` digest matches its receipt. I reran a copy of the replay with the output path redirected to a fresh directory; all 144 fixtures pass.

The fixture matrix covers six index values, including low-byte truncation, flag values 0/1/255, incoming PRIMASK 0/1, and base words 0/10/127/`0xFFFFFFFF`. With a nonzero flag, the original code writes the low-byte index then sets pending to 1. Otherwise it calls original `0x42CDF8` using that low byte; the child field write matches the stated fixture arithmetic. The child result is ignored. The epilogue returns saved PRIMASK in R0 and incoming R3 in R1, while preserving R4 and SP.

The pending helper is tested only with gate=1, mode=3, boost=15 and a fixed destination. Stable fixture memory is assumed; physical meaning, concurrent mutation, and caller ownership remain open. No canonical admission is claimed.
