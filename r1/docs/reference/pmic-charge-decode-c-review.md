# PMIC charger condition reconstructed in C

Current implementation: [ordinary C PMIC status ABI](pmic-pure-c-review.md). Scratch-register/frame preservation described below is historical.

`board/native_pmic_charge_decode.c` supplies the previously unowned stock
`0x5061c` routine and its byte-write wrapper at `0x35766`. One manifest candidate
unit owns both functions; no duplicate stock implementation is added.

The decoder always reads registers 5, 6 and 7 in that order, ignoring transport
return statuses. It returns zero unless register 6's high nibble equals 12,
register 5's top three bits equal 5, and register 7's high bit is clear. When
all three conditions hold, it reads register 3, sets bit 6 if absent, writes
that modified byte, and returns one regardless of the transport result.

The native scratch words alias saved incoming R0–R3. C preserves the incoming
high bytes and clears only each destination's low byte before reading. Empty
register constraints and the shared SP helper preserve native frame positions
for the configured Clang profile: 24 bytes at each read and 40 bytes at the
nested write provider. The byte-write adapter passes one byte from its saved
value word and restores callback-mutated frame words to R2/R3.

The product object passes 48,504 paired stock/C cases over 2,021 input vectors.
Each register's full byte domain is exercised against a condition-satisfying
baseline, plus seeded mixed vectors. The suite covers byte/full-word/no-write
reads, success/error returns, two incoming register seeds and controlled
cross-scratch mutations. It compares ordered provider calls, exposed root
frames, live R4–R11, returns, final root scratch, SP and interrupt masks.
Wrong nibble, wrong set bit and full-word-zero mutations are all rejected.

All 580 R1 units compile; all 579 preceding objects remain identical. Imports
remain 164 application / 34 bootloader. This candidate does not enter the exact
source plan: its initial save order differs from stock. Nested private return
addresses are excluded from comparison. Transport providers are modeled, the
byte-write adapter is tested only through this decoder, and physical hardware,
arbitrary aliases, faults and concurrency are unproven. REA bytes, reproducible
probes and counterexamples are under `build/goal-r1-pmic-charge-decode`; durable
results are in the adjacent JSON.
