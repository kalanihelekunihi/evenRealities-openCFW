# GX8002 UART boot stage-1 PMU descriptor-fill leaf (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime `0x10000000..0x10002000`).
Prior passes decoded the span (`gx8002-uart-boot-stage1-cd001-analysis.md`)
and closed the arithmetic/noop leaves (128 stock bytes), the reset prologue
(48), four PMU trim-bit leaves (72), four polled-UART leaves (124), the
ID-cell/clock-source leaves (42), and the XIP transfer leaves (256).
This tranche closes one further leaf as production-routed reviewed source
in the experimental codec candidate: **180 stock bytes replaced by 142
compiled bytes plus 38 generated fill bytes**.

## Envelope

| Symbol | Runtime | Package | Stock | Compiled | Kind |
| --- | --- | --- | --- | --- | --- |
| `open_cfw_gx8002_uart_stage1_pmu_fill_desc` | `0x10000780` | `0x7D0` | 180 | 142 | compiled_c |

The envelope is the routine body `0x10000780..0x10000834` only. The
12-byte literal pool at runtime `0x10000834..0x10000840` (words
`0x20002018`, `0xA0300088`, `0xA001008C`, each confirmed by reading the
package bytes) stays retained stock: the C synthesizes every constant
with `movi`/`bseti`/`movih`/`ori`, so no literal pool is emitted. The
preceding 12-byte thunk at `0x10000774..0x10000780` (adds dead
accumulations to `r0`, loads the id from the literal at package `0x1EAC`,
sets `r6`, falls through) is a separate caller entry and is not claimed.

Behavior, in upstream terms (peripheral table at `0x20002018`, 26
16-byte entries; MCU config domain `GX_REG_BASE_MCU_CONFIG`, PMU config
domain `GX_REG_BASE_PMU_CONFIG`):

- Gate: `id > 25` or null descriptor returns `0xFFFFFFFF` (the stock
  `cmphs`/`bez` pair; the compiled C reproduces both with the same
  branch structure).
- `desc[0] = 0`, then match order: direct hit (`table[id] == id`),
  entry-0 fallback (`table[0] == id`), linear scan of entries 1..25
  (stock `bnezad` loop, 25 iterations); first match wins and its entry
  address (`base + slot * 16`) is stored to `desc[0]`, else return
  `0xFFFFFFFF`. The duplicate `table[0]` read when `id == 0` hits
  directly is preserved in the trace.
- Domain select: `id < 10` fills the PMU words (`0xA0010000`,
  `0xA001008C` = `PMU_CFG_SOURCE_SEL0`, `+0x18/+0x1C/+0x20` =
  `PMU_CFG_MEPG_CLK_INHIBIT_NORM/1SET/1CLR`); `id >= 10` fills the MCU
  words (`0xA0300000`, `0xA0300088` = `MCU_CFG_SOURCE_SEL`, same inhibit
  triple). The stock falls through to the MCU stores when `cmphsi id,
  10` holds (repo `cmphsi` convention: unsigned `>=`); an earlier draft
  had the domains backwards and the battery caught it. The two stock
  tails are folded into one selected tail; stored values and order are
  identical. `desc[5]` is `base | 0x20` (bit 5 already set, matching the
  stock `bseti`). Success returns 0.
- Dropped: the stock's redundant null check on the computed (never null)
  entry address. The descriptor pointer is `volatile` in the C so the
  six stores keep stock order (an earlier non-volatile draft stored
  `desc[2..4]` before `desc[1]` and the battery caught it).

## Provenance

Clean-room MIT C in
`components/shared/gx8002/runtime_gx8002_uart_stage1_pmufill.c`, against
the pinned NationalChip grus SDK `arch/soc/grus/include/base_addr.h`
(commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, blob recorded by the
verifier; SDK repo-level MIT LICENSE blob
`37a1e362999f2040c2c0cda1a3231b6b5913efbf`). Only the numeric domain
bases and register offsets cross the boundary; the table base/stride,
the match order, and the `id < 10` split were recovered from the decoded
stock control flow. No SDK text is reproduced. See
`NATIONALCHIP-UART-BOOT-STAGE1-PMUFILL-NOTICE.txt`.

## Verification

`g2/tools/verify_gx8002_uart_stage1_pmufill.py` (report
`docs/research/gx8002-uart-stage1-pmufill-verification.json`, 2,438 cases):

- Compiles the C with `-Os -mcpu=ck804ef -mhard-float -ffreestanding
  -fno-builtin -ffunction-sections -fdata-sections -fno-tree-loop-optimize`,
  links the section at its runtime entry into one `pmufill.elf` with no
  undefined symbols and no relocations; the 142-byte section fits the
  180-byte envelope at aligned package offset `0x7D0`.
- The stock span is rewrapped with the CK804EF ELF flags and shifted to
  its runtime base (the `gx8002-uart-boot-stage1-cd001-analysis.md`
  recipe) so decoded addresses are absolute on both sides.
- Decoded-target execution of stock vs linked body over a flat word-RAM
  model (peripheral table + descriptor cells; unmodeled addresses trap):
  identical exact access traces (kind, address, width, value of every
  read/write), identical `r0`, identical final RAM, callee-saved
  registers preserved.
- Independent Python oracle on every case: gate, zero store, match
  order, entry address, domain-selected six-word fill, stated from the
  decoded structure rather than the decoded instructions.
- Battery: 38 table shapes (identity, zeros, ones, entry-0-only, scan
  hits at 1/9/10/24/25, single-hit-per-slot for all 26 slots,
  direct-beats-scan and entry-0-beats-scan duplicates, id-0-via-entry-17,
  strided) x ids {0..26, 31, 255, 256, 0x80000000, 0xFFFFFFFF} x two
  descriptor arenas, plus six null-descriptor cases.
- `g2/tests/test_gx8002_uart_stage1_pmufill.py` (11 tests): host
  execution of the C leaf against a redirected table (documents the
  32-bit entry-address truncation on the 64-bit host), interpreter unit
  checks for the newly exercised opcodes (`bnezad`, `incf`, `cmphsi`,
  `cmpnei`, indexed `ldr.w`, three-operand `bseti`, `ori`),
  stock-envelope regression, and fit/no-relocation regression.
- New interpreter opcodes follow established repo conventions (`cmphsi`
  as unsigned `>=`, `incf` as assign-if-false, `bnezad` as
  decrement-then-branch-if-nonzero); each is pinned by stock/source
  agreement on every battery case, not just by convention.

Accepted boundary (documented, not verified): the peripheral table is
modeled RAM, not hardware state; the 12-byte literal pool and the
caller thunk stay retained; concurrent table mutation and timing are
unmodeled. Hardware timing and whole-device behavior remain unqualified
(`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-pmufill` in
`tools/build_gx8002_source_candidate.py` (artifact `pmufill.elf`,
baseline above) and in the `gx8002-source-candidate` test list in
`g2/Makefile`. The shared `make -C g2 gx8002-source-candidate` gate was
not run here: it currently fails before reaching any stage-1 tranche at
a pre-existing stale baseline owned elsewhere (same `rtc-init` pin drift
reported by the prior tranche; left for its owner). Tranche admission
was verified through the builder's exact `reviewed_replacements` +
`compose` path in a private output dir: 1 replacement, 142 compiled
bytes + 38 generated fill, ownership split at package `0x7D0..0x884`,
firmware size unchanged. The generated
`gx8002-source-candidate-build.{json,md}` and experimental manifest
pins regenerate from the green shared run, so they are deliberately not
hand-edited here.

## Remains (CD-001, still retained)

CD-001 is now 850/8192 bytes source-owned (670 prior + 180 here).
Still retained: vector table (`0x10000000..0x100000FF`, blocked on
unreconstructed trap targets), init routine (`0x100001BC`), the
chip-id/early-UART routine (`0x100001FC`), the image-receive routine
(`0x100002C8`), the caller thunk at `0x10000774` plus the literal pool
at `0x10000834..0x10000840`, the baud computation (`0x100004D0`, two
retained lookup callees at `0x10000D98` / `0x10000EA0`), the configure
routine (`0x100005C4`), the checksum helper (`0x1000065C`), the handshake
loop at `0x10001DDC..`, and everything else up to `0x10002000`.
Hardware qualification stays blocked by unavailable physical evidence.
