# LIS2DW12 configuration policy in C

The configuration routine at stock `0x75510` now expresses identity/reset checks,
retry limits, sensor configuration, rate selection, final FIFO drain and dynamic
logging gates in C. REA/Ghidra confirms the complete native sequence. The former
318-byte assembly policy is replaced by C bodies plus an 18-byte entry bridge
and a 20-byte helper-call bridge. The source remains one manifest unit.

The entry bridge retains the native forty-byte scratch span at entry SP minus
64, followed by the six saved registers. The helper bridge passes and captures
all four argument/result words. This is necessary because subsequent native
register helpers can use scratch bytes seeded by incoming R2/R3. Entry addresses
are declared as assembler-named address symbols, without invented C function
prototypes or calls through incompatible types. Context callback words are
installed with separate volatile four-byte stores.

The stronger comparison also repairs an existing reconstruction mismatch. After
identity, stock computes its logging module ID and leaves R0=28, R1=the identity
byte, and R2=1 before continuing. The former assembly reconstruction replaced
the ID arithmetic with constants and left those internal register effects
unreproduced. The C register state explicitly retains them. The saved original
source is rejected by the new four-word helper-argument oracle.

Reset reads always precede a two-millisecond delay. The attempt counter is tested
before examining the reset byte: eleven polls may succeed, while the twelfth
reports failure even if that read clears the byte. Sensor helper errors are
ignored where stock ignores them. Valid initialization performs register-17,
BDU, scale, filter, FIFO and power settings in order, chooses rate 3/4/5/6 for the
stock cases, delays 100 milliseconds and drains five FIFO samples. Identity and
reset failures retain separate ring/SDK messages and live mode gates.

All 4,928 paired native/C cases pass (9,856 executions). They cover valid and
invalid identities, missing getter writes, reset-clear boundaries, delay callbacks
that change the retained reset byte, eight rate words including high-bit values,
four raw helper results, adversarial R0–R3 outputs and all 512 three-read logging
mode sequences. Every helper's four argument words, helper order, context stores,
all forty scratch bytes, return, callee-saved registers, entry SP and interrupt
masks agree. Negative controls reject the previous reconstruction, earlier
timeout, omission of the mandatory delay after reset clears and a dropped R2=1.

All 573 R1 units compile and compose without failures or duplicate strong symbols;
imports remain 197 application / 34 bootloader. `make sources-check` and
`git diff --check` pass. The unchanged canonical plan still builds a stock-identical
hybrid application, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 3,833 source-built and 642,327 unclassified binary-pull-through bytes.

Sensor/delay/logging entry points are modeled here, with controlled full-register
outputs. Private helper stack depth changes from -64 to -136/-160; arbitrary
inspection of private frames, APSR and caller-clobbered output words are outside
this receipt. Physical sensor/reset/timing behavior remains unverified. This
policy has no new byte qualification; source completeness remains false and no
G2 workflow gate advances. Source, REA, probe and build hashes are bound in
`lis-c-configuration-policy-review.json`.
