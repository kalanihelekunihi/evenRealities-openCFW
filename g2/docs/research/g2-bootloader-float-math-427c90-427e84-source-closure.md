# G2 bootloader binary32 math source closure

Date: 2026-09-01

## Result

The nine authenticated entries in `[0x00427C90,0x00427E84)` are now backed by
compilable production C at their original addresses:

- four Arm hard-float ABI veneers for `floorf`, `fmodf`, `roundf`, and `ceilf`;
- four integer-only binary32 cores preserving NaNs, infinities, signed zero,
  subnormals, and the stock rounding rules; and
- the binary32 range classifier used by the retained caller at `0x0042A9E2`.

The two freestanding translation units are
`runtime_float_math_veneers_427c90.c` and `runtime_float_math_427c90.c`.
They use no libc header, heap, mutable global, MMIO, raw instruction-byte
directive, or runtime data import. The `fmodf` reduction is a bounded MIT
adaptation of musl v1.2.5 commit
`0784374d561435f7c787a555aeab8ede699ed298`; the ABI veneers and the other
cores are openCFW clean-room compatibility implementations.

## Fixed-address layout

| Entry | Compiled bytes | Authenticated extent | Retained tail |
|---|---:|---:|---:|
| `floorf_427c90` | 16 | 16 | 0 |
| `floor_bits_427ca0` | 44 | 44 | 0 |
| `fmodf_427ccc` | 16 | 16 | 0 |
| `fmod_bits_427cdc` | 168 | 188 | 20 |
| `roundf_427d98` | 16 | 16 | 0 |
| `round_bits_427da8` | 40 | 40 | 0 |
| `ceilf_427dd0` | 16 | 16 | 0 |
| `ceil_bits_427de0` | 44 | 44 | 0 |
| `float_range_classify_427e0c` | 72 | 120 | 48 |

Both reviewed compiler profiles emit the same 432 source bytes. The four
veneer relocations are strict `R_ARM_THM_CALL` bindings to the adjacent
integer cores. The floor, round, and ceiling cores plus all four veneers are
byte-exact with the authenticated stock spans. The independently maintained
remainder and classifier implementations are smaller and leave 68 bytes of
authenticated suffix typed as unreachable. No direct interior call or stored
Thumb pointer reaches either suffix.

## Behavioral evidence

`tests/test_runtime_bootloader_float_math_427c90.py` checks:

- boundary values around zero, one-half, one, `2^23`, and `2^24`;
- positive and negative zero, subnormal values, infinities, and NaN payloads;
- 30,000 deterministic random binary32 inputs for each rounding core;
- 75,000 deterministic random binary32 operand pairs for remainder;
- 30,000 deterministic random classifier inputs plus every range boundary;
- canonical invalid-remainder output `0x7FFFFFFF`; and
- dual-profile section sizes, relocations, address-window fit, and the seven
  stock-exact leaves.

The existing GCD, ratio, and multiplier host suites also pass after their C
provider declarations and strict relocation symbols were renamed from
`retained_*` to the source-owned entry names. The emitted firmware bytes do
not change from that symbol-ownership rename.

The exhaustive post-MSPI ledger is now 267 spans and 57,153 conserved bytes:
46 source spans / 5,922 bytes, 37 exact cross-image candidates / 2,756 bytes,
102 typed unresolved executable spans / 17,194 bytes, 16 unreachable tails /
284 bytes, two retained-data spans / 28 bytes, and 64 typed non-entry spans /
30,969 bytes. There are zero unclassified bytes. The next executable frontier
is `0x00428378`, after the typed non-entry interval
`[0x00427E84,0x00428378)`.

## Production evidence

The Apple provider is 163,840 bytes with SHA-256
`94afbc3d7e1aa8d0d21095de081523c2ed9e422287355128eb20d36bf27c88e2`.
Its accounting is 38,263 source-owned bytes, 108,731 retained bytes, 16
alignment bytes, and 16,830 generated patch-site bytes; 20,444 source bytes
are compiled in place and 2,594 are compiled in reviewed caves. The Linux
provider is 163,824 bytes with SHA-256
`426d77749f96307ae9a45173d20684570d5994d902cf1f1f5cb01f935c6ba7c6`.

`tools/integrate_g2_bootloader_float_math_427c90.py` owns the nine source
registrations and exhaustive census split. The central bootloader manifest
synchronizer emits distinct source regions and retained suffixes from the
live provider contract.

## Physical evidence boundary

No authorized G2 hardware is available in this workspace. Live FP exception
flags, rounding-mode interaction, caller timing, downstream display/clock
behavior, reset, and cold-boot validation are therefore exactly **blocked by
unavailable physical evidence**. No signing, flashing, reset, live register
access, or other hardware operation occurred. Firmware-wide functional
completeness is not claimed.
