# Independent review 6325 — correction

Disposition: **PASS_SCOPED**; `accepted:false`. This /002 report supersedes /001; the prior return statement was incorrect.

The wrapper at 0x42D5CC–0x42D5F8 saves R2–R4/LR, calls 0x41B8EC, and stores its result through SP0, replacing the incoming R2 slot. It freshly reads the deferred flag; if nonzero it calls 0xCDF8 with a fresh selector byte (ignored result) and stores zero to the flag. It then always stores zero to the other literal-selected byte, reloads the saved SP0 value, restores PRIMASK with MSR, sets R0 to zero, and pops R1, R2, R4, and PC. Thus the saved mask is restored but is not the return value.

The adjacent leaf at 0x42D5F8–0x42D61E checks a fresh guard byte; on nonzero it reads a low-seven-bit field, compares unsigned with 8, and, when the threshold is met, performs a second fresh read and subtracts 7; otherwise it uses zero. It inserts that result into bits 10–16 of a fresh word and stores it, then returns zero. A changed second read may underflow before BFI truncation.

Hashes and GNU Thumb boundaries match the locked source. Static evidence only; no hardware/runtime/C-equivalence/admission claims, and no canonical files or gates changed.
