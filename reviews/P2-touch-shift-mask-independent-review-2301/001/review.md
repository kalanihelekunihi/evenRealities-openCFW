# Independent review 2301

**Result:** PASS_SCOPED.

Isolated replay regenerated all 4,160 fixtures. Source, 14-byte body [0x6262,0x6270), and candidate file hashes match. Decode confirms the shift amount is the wrapped 32-bit sum of (R0 & 3), R1, and 1; LSLS uses register-shift low-eight-bit semantics: zero returns one, 1–31 returns the corresponding single bit, and counts of at least 32 return zero. R1/R2/R4/SP preservation assertions pass.

**Limits:** Inputs cover each offset byte and selected overflow offsets with all sixteen low-two-bit source patterns, not all possible 32-bit pairs. Physical meaning of the mask and memory/fault behavior are outside this leaf. No canonical admission.
