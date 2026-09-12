# G2 bootloader BL-009 trim-state leaves source closure (partial)

Status: 6 in-place leaves (210 bytes) + 1 in-place data group (36 bytes)
landed and production-routed; remainder triaged below. No hardware
operation. Hardware qualification stays blocked by unavailable
physical evidence.

## Scope

BL-009 assigns 25 disjoint `official_blob` spans totalling 5,978 bytes
in `0x0042B9BA..0x00430470`. The census
(`g2-bootloader-gap-census-42b9ba-430470.md`) and the gap-literal pass
(`g2-bootloader-bl009-gap-literals-source-closure.md`, 334 bytes
routed) left 5,644 bytes retained. This pass closes 246 more bytes
inside the `0x0042D5C2..0x0042D84C` span: six self-contained Thumb-2
leaves and the nine attributable cells of the shared literal pool at
`0x0042D79E..0x0042D848` they read. BL-009 source-owned total is now
580 of 5,978 bytes.

## Routed functions (210 bytes)

All six live in `components/bootloader/core_overlay/
runtime_bl009_trim_state_leaves_42d5c2.c` (MIT): exact naked-asm
bodies plus portable C behavior models. Each body is byte-identical
under both reviewed toolchains (Apple clang 21.0.0,
`-enable-machine-outliner=never`; Homebrew clang 22.1.8), carries zero
relocations, and is byte-identical to its Apollo main analogue, which
corroborates the reconstruction:

| Entry | Bytes | Body SHA-256 | Main analogue | Behavior |
| --- | ---: | --- | --- | --- |
| `..._state_flag_raise_42d5c2` | 10 | `25ecf9ae...eaea5` | `0x005A07E6` | store 1 to retained state-flag byte, return 0 |
| `..._trim_field_publish_42d5f8` | 38 | `6d2402da...30f509d` | `0x005A081C` | if gate flag set, publish `(level >= 8 ? level-7 : 0)` into LDOREG1 bits 9:0 |
| `..._trim_fields_set_42d61e` | 28 | `8ba3e01b...ffd88937` | `0x005A0842` | set field 1 in bits 5:0 of `0x40020088`, field 2 in bits 16:15 of `0x400201B0` |
| `..._trim_block_program_42d63a` | 88 | `f2b1e6d2...0c2acb` | `0x005A085E` | clear `0x400211A0` bits 12:8, store 1000 into bits 31:16, store 0/800/450/600/250 into `A8/A4/AC/B4/BC`, clear bits 1:0 of head |
| `..._trim_bits_raise_42d692` | 20 | `3b333cb5...4aa4d39035` | `0x005A08B6` | set `0x400211A0` bits 1:0, raise state-flag byte |
| `..._trim_bits_clear_42d6a6` | 26 | `91ded6f9...405e739f43` | `0x005A08CA` | if flag set, clear `0x400211A0` bits 1:0 and lower the flag |

`0x40020080` is the LDOREG1 power-trim register identified by the
SPOTmgr transition closure; `0x400201B0` is the global-control
register; `0x400211A0..0x400211BC` is a six-word peripheral register
block programmed with fixed calibration constants. The portable
models take state/MMIO locations as parameters and are checked over
1,800 randomized register/flag cases plus boundary levels.

## Routed pool cells (36 bytes)

`runtime_bl009_trim_pool_42d7e0.c` (MIT) reproduces nine
peripheral-address words (`0x42D7E0`, `0x42D7E8`, `0x42D7FC`,
`0x42D818..0x42D82C`) as one 36-byte payload in nine placements
(sha `e5982a52...042b4e`, identical under both toolchains). The
pool's four SRAM-address cells (`0x42D7A0`, `0x42D7BC`,
`0x42D814`, `0x42D830`) stay retained per the unattributed-SRAM rule;
the portable leaf models do not depend on those addresses.

## Deliberately not routed

- `0x0042D5CC` (44 bytes with its pad): calls `0x0041B8EC`, still
  opaque inside BL-005. Cannot close as a typed provider either.
- `0x0042D6C0` (220-byte dispatcher) plus the pool head it shares:
  self-contained (no `bl`), but a 15-load multi-condition body that
  needs its own dedicated reconstruction pass with differential
  testing; deferred, not blocked.
- The remaining six code spans, pointer tables into BL-012/BL-005,
  and unattributed cells documented by the two prior audits.

## Verification

- `g2/tests/test_runtime_bootloader_bl009_trim_leaves_42d5c2.py`
  (9 tests): portable behavior incl. 1,800 randomized cases,
  dual-toolchain byte-exactness against stock and main analogues,
  pool-payload match, overlay-pin check, MIT/no-raw-encoding review.
- Component build: 331 in-place leaves + 78 data groups verify clean;
  the built provider is byte-identical to stock across the whole
  BL-009 window (0 diffs in `0x0042B9BA..0x00430470`).
- `test_bootloader_core_overlay.py` (incl. the provider-contract
  test after syncing the 1 stale manifest blob into the 21 observed
  regions; regions tile exactly) and
  `test_bootloader_bl009_gap_literals.py`: 27 tests green.
- Shared `make -C g2 source` / flash-plan regeneration stays blocked
  by other lanes' uncommitted apollo_main/manifest changes
  (littlefs-snapshot pin failure; package pin desync observed
  `262aacb1` vs pinned reference), unrelated to this byte-neutral
  pass. No hardware operation occurred.

## Follow-ups for a re-run of BL-009

1. Reconstruct the `0x0042D6C0` dispatcher (220 bytes, no opaque
   callees) with host differential tests.
2. Close `0x0042D5CC` once BL-005 lands `0x0041B8EC`.
3. Attribute the four retained SRAM pool cells, then route them.
4. Continue the remaining code spans / pointer tables per the prior
   audits (needs BL-005/BL-011/BL-012).
