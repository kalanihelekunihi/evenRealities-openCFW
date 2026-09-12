# GX8002 UART boot stage-1 polled-UART leaves (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime `0x10000000..0x10002000`).
Prior passes decoded the span (`gx8002-uart-boot-stage1-cd001-analysis.md`),
closed three arithmetic/noop leaves as reviewed C
(`gx8002-uart-stage1-divmod-source.md`: 128 stock bytes), the reset prologue
as reviewed assembly (`gx8002-uart-stage1-reset-source.md`: 48 stock bytes),
and four PMU trim-bit leaves (`gx8002-uart-stage1-pmubits-source.md`: 72
stock bytes). This tranche closes four polled-UART register leaves as
production-routed reviewed source in the experimental codec candidate:
**124 stock bytes replaced by 124 compiled bytes, zero fill**.

## Envelopes

| Symbol | Runtime | Package | Stock | Compiled | Kind |
| --- | --- | --- | --- | --- | --- |
| `open_cfw_gx8002_uart_stage1_put` | `0x10000584` | `0x5d4` | 28 | 28 | compiled_c |
| `open_cfw_gx8002_uart_stage1_put_sync` | `0x100005a0` | `0x5f0` | 36 | 36 | compiled_assembly |
| `open_cfw_gx8002_uart_stage1_try_get` | `0x10000620` | `0x670` | 32 | 32 | compiled_c |
| `open_cfw_gx8002_uart_stage1_get_char` | `0x10000640` | `0x690` | 28 | 28 | compiled_c |

Each envelope is 24–32 bytes of code plus the 4-byte base-cell literal pool
(the word `0x20002014`, the linked image's `dw_serialbase` variable). Every
pool word is referenced only by its own function's `lrw` (full-span scan:
`0x59c` only from `0x584`, `0x5c0` only from `0x5a0`, `0x63c` only from
`0x620`, `0x658` only from `0x640`), so each envelope is self-contained.
The C bodies synthesize the cell address with `movi`/`bseti` and need no
pool; they fill their whole envelopes with code, hence zero fill.

Behavior, in upstream terms:

- `put`: blocking transmit — poll LSR bit 6 (transmitter-empty), word-store
  the argument to THR. Preserves `r0`.
- `put_sync`: blocking transmit-then-wait — poll, store, poll again.
- `try_get`: non-blocking receive probe — single LSR read; if bit 0
  (data-ready) is set, word-read RBR, byte-store to `*c`, return 0, else
  return -1 without touching `*c`.
- `get_char`: blocking receive — poll bit 0, word-read RBR, return the
  zero-extended low byte.

## Provenance

Clean-room MIT C in
`components/shared/gx8002/runtime_gx8002_uart_stage1_serial.c` (three
leaves) plus clean-room MIT assembly in
`components/shared/gx8002/runtime_gx8002_uart_stage1_putsync.S`
(`put_sync`), identified against the pinned NationalChip grus SDK
`arch/soc/grus/spl/spl_uart.c` (`serial_put`, `serial_put_sync`,
`serial_try_get`, `serial_get_char` at commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, blob
`f1f58e164149513866aa47c5c6810fed6d0f4d5c`) and the MIT register header
`arch/soc/grus/include/base_addr.h` (blob
`536d2e51e19f12f3a7f4e354fba53be906e05702`; SDK repo-level MIT LICENSE
blob `37a1e362999f2040c2c0cda1a3231b6b5913efbf`). Only numeric register
offsets (LSR `0x14`, data `0x0`), bit positions (TEMT 6, DR 0), and the
call/return conventions cross the boundary; the bodies were written from
the decoded stock control flow. The GPL-licensed SDK headers (`common.h`,
`spl/spl.h`) were deliberately not used: no SDK text is reproduced. See
`NATIONALCHIP-UART-BOOT-STAGE1-SERIAL-NOTICE.txt`.

Assembly was used for exactly one leaf: every probed C shape for the
two-loop `put_sync` body compiles to 38 bytes against the 36-byte stock
envelope (the allocator spills the first-loop status load into a high
register, costing a 4-byte `ld.w` where the stock toolchain used a 2-byte
one), across `-Os`/`-O2` with and without `-fno-tree-loop-optimize`,
`-fno-gcse`, and `-fno-guess-branch-probability`. The assembled `put_sync`
bytes are additionally byte-identical to the stock envelope (pinned by
test), but admission rests on decoded-trace equivalence like every other
tranche.

## Verification

`g2/tools/verify_gx8002_uart_stage1_serial.py` (report
`docs/research/gx8002-uart-stage1-serial-verification.json`, 476 cases):

- Compiles the C with `-Os -mcpu=ck804ef -mhard-float -ffreestanding
  -fno-builtin -ffunction-sections -fdata-sections -fno-tree-loop-optimize`,
  assembles the `.S` with `-mcpu=ck804ef -mhard-float`, links all four
  sections at their runtime entries into one `serial.elf` with no undefined
  symbols and no relocations; each section exactly fills its stock envelope
  at an aligned package offset.
- The stock span is rewrapped with the CK804EF ELF flags and shifted to its
  runtime base (the `gx8002-uart-boot-stage1-cd001-analysis.md` recipe) so
  decoded branch targets are absolute on both sides.
- Decoded-target execution of stock vs linked bodies with a scripted UART
  model (base cell fixed per case over both UART bases; LSR/RBR read scripts
  with hold-last; transmit writes recorded; destination word modeled):
  identical `r0`, identical destination word, identical transmit writes, and
  identical exact access traces (address, width, value of every read/write),
  callee-saved registers preserved, no traffic outside the cell, the
  destination word, and the two UART registers.
- Independent Python oracle for all four values on every case: put covers 6
  characters (including a full-word `0x12345678` pinning the word store) × 5
  poll scripts × 2 bases; put_sync covers 6 × 3 first-poll × 3 second-poll
  × 2 bases; try_get covers 8 LSR states × 4 RBR words (including high-bit
  narrowing) × 2 destination seeds × 2 bases; get_char covers 5 poll scripts
  × 6 RBR words × 3 `r0` seeds × 2 bases.
- `g2/tests/test_gx8002_uart_stage1_serial.py` (10 tests): host execution
  of the three C leaves against a redirected UART (the base-cell macro is
  overridable; `uintptr_t` locals keep the full host address), interpreter
  unit checks for the new opcodes and access widths, stock-envelope
  regression, fit/no-relocation regression, and the put_sync byte-identity
  pin.

Accepted boundary (documented, not verified): poll loops are verified only
over finite scripts; LSR/RBR have no external concurrent updates in the
model; the base-cell word is fixed per case. Hardware timing and
whole-device behavior remain unqualified (`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-serial` in
`tools/build_gx8002_source_candidate.py` (artifact `serial.elf`, baseline
above) and in the `gx8002-source-candidate` test list in `g2/Makefile`.
`make -C g2 gx8002-source-candidate` and
`make -C g2 codec-source-experimental` pass; ownership splits the former
`retained_stock` spans at package `0x5d4..0x5f0`, `0x5f0..0x614`,
`0x670..0x690`, and `0x690..0x6ac` into three `compiled_c` sections plus one
`compiled_assembly` section with no fill.

## Remains (CD-001, still retained)

CD-001 is now 372/8192 bytes source-owned (128 divmod + 48 reset + 72
pmubits + 124 here). Still retained: vector table
(`0x10000000..0x100000ff`, blocked on unreconstructed trap targets), init
routine (`0x100001bc`), baud computation (`0x100004d0`, two retained lookup
callees), the configure routine (`0x100005c4`, calls out to `0x10000d98`
and the baud routine), the handshake/receive loop, and everything else up
to `0x10002000`. Hardware qualification stays blocked by unavailable
physical evidence.
