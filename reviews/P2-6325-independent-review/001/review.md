# Independent review 6325

Disposition: **PASS_SCOPED**; `accepted:false`.

Hashes and Thumb boundaries match the locked source for both extents. In 0x42D5CC–0x42D5F8, the wrapper saves R2–R4/LR, calls 0x41B8EC, and stores its result through SP0, replacing the incoming R2 slot. It freshly reads the deferred flag; if nonzero it calls 0xCDF8 with a fresh selector byte (ignored result) and stores zero to the flag. It then always stores zero to the other literal-selected byte, reloads the saved SP0 value, restores PRIMASK with MSR, and returns that value in R0 while popping R1, R2, and R4. In 0x42D5F8–0x42D61E, a fresh guard byte controls whether it reads the selected word; the low-seven-bit value is compared unsigned with 8, and a second fresh read is reduced by 7 when the threshold is met, otherwise zero is used. A fresh hardware word receives that value in bits 10–16 and is stored; return is zero.

The second field read can differ from the first, and its subtraction can wrap before BFI truncates it; those effects are retained. No hardware meaning, runtime result, C equivalence, or admission is claimed. No canonical artifact or gate changed.
