# G2 bootloader BL-009 state-flag dispatcher source closure (partial)

Status: 1 in-place leaf (222 bytes) + 1 in-place data group (8 bytes)
landed and production-routed; remainder triaged below. No hardware
operation. Hardware qualification stays blocked by unavailable
physical evidence.

## Scope

BL-009 assigns 25 disjoint `official_blob` spans totalling 5,978 bytes
in `0x0042B9BA..0x00430470`. The census
(`g2-bootloader-gap-census-42b9ba-430470.md`), the gap-literal pass
(`g2-bootloader-bl009-gap-literals-source-closure.md`, 334 bytes
routed), and the trim-leaves pass
(`g2-bootloader-bl009-trim-leaves-42d5c2-source-closure.md`, 246
bytes routed) left 5,398 bytes retained. This pass closes 230 more
bytes inside the `0x0042D5C2..0x0042D84C` span: the self-contained
dispatcher at `0x0042D6C0..0x0042D79E` and the two attributable
cells of the shared literal pool it reads. BL-009 source-owned
total is now 810 of 5,978 bytes.

## Routed function (222 bytes)

`components/bootloader/core_overlay/
runtime_bl009_state_dispatch_42d6c0.c` (MIT) holds an exact
naked-asm body plus a portable C behavior model for
`open_cfw_bootloader_state_flag_dispatch_42d6c0` (entry
`0x0042D6C0`, size 222, sha
`39812d74...41f37325b`). The body is byte-identical under both
reviewed toolchains (Apple clang 21.0.0,
`-enable-machine-outliner=never`; Homebrew clang 22.1.8), carries
zero relocations, and is byte-identical to its Apollo main analogue
at `0x005A08E4`, which corroborates the reconstruction.

Semantics (no arguments, no calls, returns 0; three retained SRAM
flag bytes published):

| Flag | Set condition (mode = low byte of `0x4002000C`, state = SRAM word) |
| --- | --- |
| one (`0x200271B3`) | mode `0x21`, state 2 |
| two (`0x200271B4`) | (mode `0x21`, state 2 or 3) or (mode `0x22`, state 0) |
| three (`0x200271B5`) | (mode `0x22`, state 1) or (mode `0x23`, state 0, guard clear) |

The guard reads the status word, masks it with `0x3FE00000`,
requires a zero low halfword, and additionally requires either a
masked match of `0x31800000` with bits 20:16 at or above `0x14`,
or bits 29:25 at or above `0x19`. The minimized predicate was
derived by tracing all four guard sub-paths (`guard_set`,
`guard_one`, `guard_zero`, fall-through) and is covered by
floor/ceiling boundary cases on both fields.

## Routed pool cells (8 bytes)

`runtime_bl009_dispatch_pool_42d834.c` (MIT) reproduces the two
identified scalar cells the dispatcher loads as one 8-byte payload
in two placements (sha `f107a364...ca33eb58e`, identical under both
toolchains):

- `0x0042D834` = `0x4002000C`, trim-block state register in the
  same `0x400200xx` power-trim block as the routed LDOREG1 cells;
  loaded once into r2 (original `ldr` at `0x0042D6C2`) and read
  indirectly at five sites.
- `0x0042D840` = `0x3FE00000`, field mask ANDed with the guarded
  status word (original `ldr` at `0x0042D750`).

The dispatcher's five SRAM-address cells (`0x0042D7AC`,
`0x0042D810`, `0x0042D838`, `0x0042D83C`, `0x0042D844`) stay
retained per the unattributed-SRAM rule; the portable model takes
every address-fed value as a parameter.

## Deliberately not routed

- `0x0042D5CC` (44 bytes with its pad): calls `0x0041B8EC`, still
  opaque inside BL-005. Cannot close as a typed provider either.
- `0x0042D848` (4 bytes, `movs r0, #0; bx lr`): decodes as a
  return-zero tail between the pool end and the stream-mode
  primitive, but no caller or entry evidence attributes it to a
  function; left retained rather than labelled without evidence.
- The remaining six code spans, pointer tables into BL-012/BL-005,
  and unattributed cells documented by the three prior audits.

## Verification

- `g2/tests/test_runtime_bootloader_bl009_dispatch_42d6c0.py`
  (8 tests): portable behavior incl. 2,000 randomized cases against
  an independently transcribed expectation plus mode/state/guard
  boundaries, dual-toolchain byte-exactness against stock and the
  main analogue, literal-referent scan (literal sites plus the five
  indirect readers), pool-payload match, overlay-pin check,
  MIT/no-raw-encoding review.
- Component build (`make -C g2 bootloader-component`): recorded in
  the progress entry; provider byte-identity across the BL-009
  window checked there.
- `test_bootloader_core_overlay.py` and
  `test_bootloader_bl009_gap_literals.py`: recorded in the progress
  entry.
- Shared `make -C g2 source` / flash-plan regeneration: owned by
  other lanes while apollo_main/manifest changes are uncommitted;
  recorded in the progress entry. No hardware operation occurred.

## Follow-ups for a re-run of BL-009

1. Close `0x0042D5CC` once BL-005 lands `0x0041B8EC`.
2. Attribute the return-zero tail at `0x0042D848` (or fold it into
   an adjacent span's pass) and the remaining unattributed SRAM
   cells, then route.
3. Continue the remaining code spans / pointer tables per the prior
   audits (needs BL-005/BL-011/BL-012).
