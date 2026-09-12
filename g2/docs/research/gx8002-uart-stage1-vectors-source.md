# GX8002 UART boot stage-1 vector table and trap entries (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime `0x10000000..0x10002000`).
Prior passes decoded the span (`gx8002-uart-boot-stage1-cd001-analysis.md`)
and closed the arithmetic/noop leaves, the reset prologue (48B at package
`0x150`), four PMU trim-bit leaves (72), four polled-UART leaves (124),
the ID-cell/clock-source leaves (42), the XIP transfer leaves (256), and
the PMU descriptor-fill leaf (180). The PMU-fill audit left the vector
table (`0x10000000..0x100000FF`) retained as "blocked on unreconstructed
trap targets". This tranche closes it together with both trap targets as
production-routed reviewed assembly in the experimental codec candidate:
**264 stock bytes replaced by 264 linked bytes (256 data + 8 code),
zero fill**.

## Envelope

| Symbol | Runtime | Package | Stock | Linked | Kind |
| --- | --- | --- | --- | --- | --- |
| `open_cfw_gx8002_uart_stage1_vectors` | `0x10000000` | `0x50` | 256 | 256 | generated_source_data |
| `open_cfw_gx8002_uart_stage1_traps` | `0x10000130` | `0x180` | 8 | 8 | compiled_assembly |

The stock bytes authenticate the structure exactly: 64 little-endian
words with value `0x10000100` once (word 0), `0x10000130` 31 times
(words 1..31), and `0x10000134` 32 times (words 32..63), followed by
`04 00 00 00 04 00 00 00` (two CK804 `br`-to-self halfwords, each with
a 2-byte zero pad). The table is therefore fully determined by three
addresses; the source spells one `.word` per address and expands the
repetitions with `.rept 31` / `.rept 32`, so a miscount would fail the
byte-exact check rather than silently pass. The traps section defines
the exception/IRQ trap globals at their linked addresses, and the
table's `.word`s reference those same symbols, so table and targets
cannot drift apart. The only external input is the reset-entry address,
supplied as the absolute linker symbol
`open_cfw_gx8002_uart_stage1_reset_entry = 0x10000100` (its contents
are the reset tranche's, not claimed here).

The 2-byte zero pads after each `br` are assembler `.balign 4` fill,
matching the stock bytes. They disassemble as `bkpt` only because
`0x0000` is the CK804 breakpoint encoding; no breakpoint behavior is
claimed. The adjacent `rts` stub at runtime `0x10000138` (package
`0x188`) belongs to the divmod tranche and is untouched.

## Provenance

Clean-room MIT assembly in
`components/shared/gx8002/runtime_gx8002_uart_stage1_vectors.S`. No
upstream file is adapted: the 64-entry reset/exception/IRQ layout
follows the CK804 vector-table convention already documented for the
image-A/B stage-two bodies in
`g2-codec-stage2-section-map.tsv`, and the three addresses plus the
branch-to-self trap shape were recovered from the decoded stock bytes.
The reset-entry address agrees with the reset prologue reconstructed
in `runtime_gx8002_uart_boot_stage1_reset.S` (NationalChip lvp_kws
`spl_start.S` derivation; see
`NATIONALCHIP-UART-BOOT-STAGE1-RESET-NOTICE.txt`); no text from that
file appears here. See
`NATIONALCHIP-UART-BOOT-STAGE1-VECTORS-NOTICE.txt`.

## Verification

`g2/tools/verify_gx8002_uart_stage1_vectors.py` (report
`docs/research/gx8002-uart-stage1-vectors-verification.json`, 5 cases):

- Assembles with `-mcpu=ck804ef -mhard-float`, links the table at
  `0x10000000` and the traps at `0x10000130` into one `vectors.elf`
  with no undefined symbols and no relocations; both sections fit
  their envelopes exactly at aligned package offsets `0x50`/`0x180`.
- Both linked sections are byte-exact against the authenticated stock
  envelopes (256 + 8 bytes).
- Structure read back from the linked image: table word 0 equals the
  reset-entry symbol value, words 1..31 equal the exception-trap
  symbol value, words 32..63 equal the IRQ-trap symbol value.
- Each trap cell decodes as `br` targeting its own address with a
  zero pad halfword, and stepping the decoded branch twice returns to
  the same PC (infinite wait loop, not a fall-through).
- `g2/tests/test_gx8002_uart_stage1_vectors.py` (9 tests): source
  stays a three-address derivation (three `.word` directives plus the
  two `.rept` counts; no numeric address literals in the code region),
  link fit/flags/no-relocation regression, table-words-equal-symbols
  regression, trap self-loop decode regression, stock-envelope
  regression, and linked-payload byte-exact regression.

Accepted boundary (documented, not verified): the reset entry, the
init routine at `0x100001BC`, and the stage-2 entry at `0x10002900`
are genuine external boundaries whose contents are not reconstructed
here. Taking an exception or IRQ in stage 1 spins forever by design
of the stock image; that wait is reproduced, not qualified, and
hardware timing plus whole-device behavior remain unqualified
(`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-vectors` in
`tools/build_gx8002_source_candidate.py` (artifact `vectors.elf`,
baseline above) and in the `gx8002-source-candidate` test list in
`g2/Makefile`. The vectors section routes as the builder's
`generated_source_data` kind (non-executable section, full-envelope
payload, zero fill impossible by construction); the traps route as
`compiled_assembly`. Shared-gate status is recorded in the progress
entry; tranche admission was additionally verified through the
builder's exact `reviewed_replacements` + `compose` path in a private
output dir before any shared run. The generated
`gx8002-source-candidate-build.{json,md}` and experimental manifest
pins regenerate from the green shared run, so they are deliberately
not hand-edited here.

## Remains (CD-001, still retained)

CD-001 is now 1114/8192 bytes source-owned (850 prior + 264 here).
Still retained: init routine (`0x100001BC`), the chip-id/early-UART
routine (`0x100001FC`), the image-receive routine (`0x100002C8`), the
caller thunk at `0x10000774` plus the literal pool at
`0x10000834..0x10000840`, the baud computation (`0x100004D0`, two
retained lookup callees at `0x10000D98` / `0x10000EA0`), the configure
routine (`0x100005C4`), the checksum helper (`0x1000065C`), the
handshake loop at `0x10001DDC..`, and everything else up to
`0x10002000`. Hardware qualification stays blocked by unavailable
physical evidence.
