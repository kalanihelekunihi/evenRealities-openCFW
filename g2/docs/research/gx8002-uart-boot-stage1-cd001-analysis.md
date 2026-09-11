# GX8002 UART boot stage-one (CD-001) decode findings

Work item CD-001: package `[0x000050, 0x00002050)`, 8,192 bytes, IRAM
`0x10000000..0x10002000`, one retained span inside the larger "UART boot
stage 1 (IRAM)" region (`gx8002-stage1-wave6-boundaries.md` closed that whole
region, package `[0x00000050, 0x00002850)`, 10,240 bytes, as a typed external
boundary — `runtime_gx8002_uart_boot_stage1_boundary.c` — with no source
admission). This note records a from-scratch decoded-instruction analysis of
this item's 8,192-byte slice. **No source lands in this pass; no byte in the
range is reclassified.** `bytes_source_owned = 0`.

## Identity

- Extracted bytes (package `0x50..0x2050`, 8,192 B) SHA-256:
  `62697368925227e3d56381e285c5d7d74707b01fd3e01b9a143d8647f9934824`.
- Full stage-one body (package `0x50..0x2850`, 10,240 B) SHA-256:
  `cbbe85a2d60f5bb805dddb45fa2eac1632bdf0ab80665c040c0892c64074133f`,
  matching `OPEN_CFW_GX8002_UART_BOOT_STAGE1_SHA256_HEX`. The range is
  unchanged from the pinned value; still fully `retained_stock` per
  `docs/research/gx8002-source-candidate-build.json` (`ownership[1]`, offset
  80 size 12,692 covers this whole span and more).
- `python3 g2/tools/analyze_gx8002_upstream_objects.py` / flash-plan query
  (see item BEFORE-YOU-START step) both still show this span as `codec`
  component, `confirmed_from_uart_boot_header_and_vectors`, not source.

## Decode methodology note

`csky-unknown-elf-objdump -b binary -m csky ...` on a raw slice of
`firmware_codec.bin` mis-decodes CK804EF (abiv2) 32-bit instructions as if
they were 16-bit abiv1 opcodes — the `-b binary` target carries no ELF
`e_flags`, so the disassembler falls back to a generic/abiv1-flavoured
decode. This is **not new**: `analyze_gx8002_upstream_objects.py` and ~30
`compare_gx8002_*.py`/`build_gx8002_*_candidate.py` tools already work
around it by wrapping the slice with `objcopy -I binary -O elf32-csky-little
-B csky` and then patching the ELF header's `e_flags` (byte offset `0x24`)
to `0x21006009` (the flags an actual `csky-unknown-elf-gcc -mcpu=ck804ef`
object carries). The same fix applies to this range; it had apparently not
been applied when Wave 6 called the body "opaque" — a plain `-b binary`
disassembly of this region is unreadable garbage (`bkpt`/`cmphs` nonsense),
which is consistent with why it read as opaque without the flag fix.

Reproduce:
```sh
python3 - <<'PY'
data = open('g2/blobs/official/g2-2.2.6.10/firmware_codec.bin','rb').read()
open('/tmp/stage1.bin','wb').write(data[0x50:0x2050])
PY
g2/build/csky-macos/install/bin/csky-unknown-elf-objcopy \
  -I binary -O elf32-csky-little -B csky \
  --set-section-flags .data=alloc,code,load /tmp/stage1.bin /tmp/stage1_raw.elf
python3 - <<'PY'
import struct
b = bytearray(open('/tmp/stage1_raw.elf','rb').read())
struct.pack_into('<I', b, 0x24, 0x21006009)
open('/tmp/stage1_fixed.elf','wb').write(b)
PY
g2/build/csky-macos/install/bin/csky-unknown-elf-objcopy --adjust-vma=0x10000000 \
  /tmp/stage1_fixed.elf /tmp/stage1_vma.elf
g2/build/csky-macos/install/bin/csky-unknown-elf-objdump -D /tmp/stage1_vma.elf
```

## Confirmed structure

- `0x10000000..0x100000FF` (256 B): a standard CK804EF 64-word vector table.
  Word 0 = `0x10000100` (reset entry). Words 1..31 = `0x10000130` (one shared
  exception-trap target). Words 32..63 = `0x10000134` (one shared IRQ
  target). This matches the "64-word vector table at base" convention
  already documented for the image-A/B stage-two bodies in
  `g2-codec-stage2-section-map.tsv`, so the table itself is fully mechanical
  (derivable from three addresses) but is not yet produced from any source
  in this repo — no vector-table generator exists for any GX8002 image today
  (grepped `components/shared/gx8002/*.S` and `*.c`; none emit a table).
- `0x10000100..0x1000011D`: reset prologue. Instruction-for-instruction it is
  the same sequence already reconstructed in
  `runtime_gx8002_reset_entry.S` (mask PSR, clear a `cr<31,0>` bit, load a
  base into `cr<1,0>` [likely VBR = `0x10000000`, matching the vector table
  base], set `sp`/`r14` = `0x200027fc`, `bsr` to a local init routine, `bsr`
  to a second target). The second `bsr` target decodes as `0x10002900` —
  **256 bytes past** the end of the whole pinned 10,240-byte stage-one body
  (`0x10002800`). This is not a decode error (re-derived mechanically via
  `objdump`, not by hand-counting). The most consistent reading: stage one's
  reset handler finishes by jumping directly into **stage two's** code entry
  (`0x10002800` load address + its own 256-byte vector table = `0x10002900`),
  i.e. stage one's job is to receive stage two into IRAM at `0x10002800` over
  UART and then chain-load it. That is consistent with CD-003 covering
  `UART boot stage 2 (IRAM)` starting exactly at `0x10002800`.
- `0x1000013C` (real address): a real, called subroutine (three call sites
  at `0x1000051E`, `0x10000532`, `0x1000053A`, all `bsr 0x1000013c`). By
  decoded-instruction trace it implements 32-bit unsigned division
  (`r0` dividend, `r1` divisor → `r0` quotient) via left-align-then-restoring
  division, distinct from this toolchain's own GCC 13 libgcc `__udivsi3`
  (which uses an `ff1`-based algorithm — confirmed by disassembling
  `libgcc.a:_udivsi3.o`, no match). Division by zero returns 0 (no trap).
- `0x10000180`: a structurally parallel subroutine, called with the same
  operand convention right after each `0x1000013c` call in the routine at
  `0x100004D0`; by trace it returns the remainder (`r0 mod r1`) via the same
  align/shift loop with a `subu`/`inct` conditional-select tail instead of
  accumulating a quotient. Read together these look like a hand-written
  `udivsi`/`umodsi` pair, not compiler output.
- `0x100004D0..0x10000574`: calls the division/remainder pair together with
  two other subroutines (`bsr 0x10000ea0` with `r0=18`, `bsr 0x10000d98`
  with `r0` in `{20,21}`) to turn a UART clock/frequency id into a baud-rate
  divisor plus a `*100`-scaled fractional remainder. This is the same shape
  of computation already implemented as portable C in
  `runtime_gx8002_uart_configure.c` (divisor + fractional-remainder*16) and
  the module-id lookups resemble `runtime_gx8002_clock_frequency.c` /
  `runtime_gx8002_channel_lookup.c`. **Working hypothesis, not verified**:
  stage one reuses the same NationalChip GRUS driver source (clock, UART,
  padmux) as the main runtime, built with the reduced Kconfig described by
  `build/upstream-nationalchip-lvp-kws/uart_boot.mk`, rather than being
  bespoke bootloader code. This would make stage one closable largely by
  compiling the already-reviewed runtime sources at these addresses and
  qualifying decoded-instruction equivalence, the same way image-A/B
  functions were closed, instead of hand-authoring new C from scratch.
- `0x100001BC`: the routine called from reset (the "local init" target).
  It calls five further subroutines in sequence, then polls a routine pair
  (`bsr 0x100006d8`, `bsr 0x10000640`) waiting for a returned byte to equal
  `0x53` (ASCII `'S'`) before writing status bytes to `0x20002004` /
  `0x20002005` and returning. A single-byte `'S'`-gated wait is consistent
  with a UART boot handshake/sync byte, which lines up with the public
  `BOOT_HEAD_UART` container format referenced by `uart_boot.mk`
  (`BOOTLOADER_MAGIC_UART='02800101'`, `CONFIG_BOOT_HEADER_SERIAL_BAUD_RATE`)
  even though that header format itself is host-side tooling, not this
  firmware body.

## What remains

None of the above is compiled, linked, or verified against the stock bytes
via the decoded-instruction execute() harness this codebase uses elsewhere
(see `verify_gx8002_uart_configure.py` for the pattern: decode both stock and
candidate, symbolically execute across a battery of inputs, compare MMIO
writes/returns — not literal byte/instruction identity). Manual tracing above
is a reading, not a proof, and per the hard rules must not be treated as
source-owned. To actually close bytes in this range, the next pass should:

1. Build a minimal `execute()` interpreter for the opcode set actually used
   here (`cmphs`, `blz`, `addu`/`cmphs`-as-carry, `lsri`, `subu`, `or`,
   `inct`, plus the MMIO-facing calls), following the existing
   `verify_gx8002_*.py` pattern, and confirm the division/remainder pair
   above against real stock-vs-candidate execution rather than hand tracing.
2. Test the "stage one reuses the main runtime's driver source" hypothesis
   directly: compile `runtime_gx8002_clock_frequency.c`,
   `runtime_gx8002_channel_lookup.c`, and `runtime_gx8002_uart_configure.c`'s
   underlying primitives with the toolchain flags implied by
   `uart_boot.mk`'s minimal Kconfig, link at the addresses found here, and
   diff decoded instructions (register-renaming tolerant).
3. Resolve the reset-handler's out-of-range second `bsr` (`0x10002900`)
   explicitly against CD-003's stage-two boundary before finalizing any
   linker layout, since a stage-one candidate build will need to place a
   real jump target there.
4. Coordinate with CD-002 (`0x10002000..0x10002800`, same official region)
   — the receive-loop body most likely spans both items' byte ranges, so
   the two should probably be reconstructed and verified as one linked unit
   even though tracked as separate work rows.

## Verification run this pass

Read-only: `csky-unknown-elf-objcopy`/`objdump` disassembly of extracted
bytes, `csky-unknown-elf-ar`/`objdump` disassembly of `libgcc.a:_udivsi3.o`
for comparison, SHA-256 recomputation of the range against pinned values,
`analyze_gx8002_upstream_objects.py`-style flash-plan/ownership cross-check.
No build, link, or test registration performed; no MMIO, flashing, or
hardware access.
