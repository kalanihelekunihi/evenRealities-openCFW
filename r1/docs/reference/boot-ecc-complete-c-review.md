# R1 ECDSA exceptional-point correction

The SDK micro-ecc backend now compiles a generated copy of the pinned upstream
C source with exactly its ECDSA verification function replaced by
`r1/src/bootloader/crypto/uecc_verify_complete.h`. The manifest records the exact
single-occurrence replacement. The upstream source, license, and arithmetic
remain unchanged; only the generated provider participates in the build.

The previous verifier used incomplete co-Z point addition for G+Q precomputation
and the Shamir accumulator. Equal x coordinates could therefore destroy the
accumulator for Q=G, Q=-G, or later additions. The replacement handles:

- infinity plus a finite affine point by initializing the accumulator;
- equal finite points through the existing Jacobian doubling routine;
- opposite finite points by representing infinity as Z=0;
- ordinary finite points through the existing co-Z addition;
- infinity precomputation entries by skipping those entries, and a final
  infinity result by rejecting the signature.

An imported public point is checked by the pinned curve-validation routine
before those group-law assumptions are used. Original scalar-range checks,
hash conversion and final x-coordinate comparison remain. The helper operates
on public verification data and makes no constant-time signing claim.

## Executed evidence

`build/sources-goal-r1-boot-ecc-complete-c/report.json` records 777/777 compiled
units with zero failures or duplicate providers. All 776 prior payload objects
are identical; the sole replaced unit is the generated micro-ecc provider.
Application imports remain 124; the bootloader has only 22 linker metadata
imports before its final layout link.

The strict GNU link produces `build/goal-r1-boot-ecc-complete-c/strict/bootloader.elf`
with no undefined symbols, using 0x59F0 (23024) FLASH bytes in the existing
0x6000-byte region: 1552 bytes remain. RAM and flash linker assertions pass.
Preprocessing confirms no inline assembly in the generated micro-ecc provider.

`verify.py` executes the final ELF and passes 213 checks over 247 calls. It tests
small private scalars 1,2,3,4, n-1 and n-2, plus four deterministic ordinary keys.
Independent cryptography verification checks every signature variant's expected
outcome before the firmware call. Cases include deterministic valid signatures,
both s representatives, corrupted inputs, endian mistakes, zero/out-of-range
scalars, wrong valid keys, short signatures and the fixed product key rejecting
foreign signatures. Known nonces 1,2,3,n-1 with hashes 0 and 1 force additional
boundary cases. A constructed u1*G+u2*Q=infinity result is rejected. Invalid
public points are rejected. Stack/core-register preservation and interrupt masks
are checked for every call.

`group-law.py` directly executes the linked mixed-add helper in 224 cases.
It compares affine outputs to independently computed cryptography P-256 points
for sums of small, negative, and ordinary scalars, including equal/opposite
operands and infinity, under four projective scales. This checks the group-law
change independently of ECDSA signature acceptance.

`defects.py` detects four separately compiled defects: missing equal-point
handling, missing infinity recovery, failure to mark opposite points as infinity,
and accepting invalid final results. The same corpus also rejects the prior
unmodified-upstream ELF on its valid generator-key regression. A clean baseline
rerun passes afterward. Probe scripts and raw receipts live under
`build/goal-r1-boot-ecc-complete-c/`; the adjacent JSON review pins their results.

R1 manifest validation passes. Global sources-check still fails on the existing
unlisted G2 `resident_rom_thumb_set.S`, which was preserved.

## Remaining proof boundaries

This closes the observed micro-ecc exceptional-point failures and broadens
verification; it is not exhaustive or formal validation of all P-256 arithmetic.
Positive vendor signatures and full reference-image hashing are now covered by
[the vendor DFU integration probe](vendor-dfu-c-review.md). Physical boot/DFU and
the complete update state machine remain required.
Timing, actual stack high-water usage, flash/settings behavior and power are
unmeasured. The application still has 124 imports and the firmware objective
remains unfinished. No device was flashed, and no byte-identity or proprietary
compiler requirement is introduced.
