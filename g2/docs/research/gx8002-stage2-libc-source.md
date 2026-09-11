# GX8002 stage-2 libc leaf source (CD-005)

Work item CD-005 covers 8,192 retained package bytes at `0x5204..0x7204`
inside `boot_stage2` (UART boot stage 2, IRAM, package `0x2850..0x958C`,
runtime `0x100051B4..0x100071B4`). This closure targets four small,
self-contained C-library leaf functions identified inside that span by
disassembling the raw package bytes with the native macOS C-SKY toolchain
(`csky-unknown-elf-objcopy -I binary -O elf32-csky-little -B csky` followed
by `objdump -D`, the same technique `verify_gx8002_padmux_get.py` and
`compare_gx8002_memset.py` use for stock comparison).

## What was found in this span

Disassembling `0x5204..0x7204` shows it is not one function: it holds the
tail of a diagnostic register-dump routine (`0x5204..0x6234`, calls a printf
wrapper at `0x61f4` that is outside this span), a device-registration helper
(`0x6234..0x62c0`), then a run of small, recognizable C-library leaves:

| Symbol (by behavior) | Package span | Bytes |
| --- | --- | --- |
| `strcmp` | `0x62c0..0x62e4` | 36 |
| `strstr`/`memmem`-style search | `0x62e4..0x6330` | 76 |
| `strchr` | `0x6330..0x634a` | 26 |
| `strlen` (word-at-a-time "hasless" trick) | `0x634c..0x6396` | 74 |
| constants `0xfefefeff`/`0x80808080` used by the strlen trick | `0x6398..0x63a0` | 8 |
| `strnlen` | `0x63a0..0x63c8` | 40 |
| `memset` (byte-align + 16-byte unrolled word fill) | `0x63c8..0x6488` | 192 |
| `memcpy` (byte-align + 16-byte unrolled word copy) | `0x648c..0x652a` | 158 |
| a second bounded byte/word search (signature differs from the `strnlen` above) | `0x652c..0x6598` | ~108 |
| itoa/ctype table dispatch used by `%d`/`%x`-style formatting | `0x6598..0x6630` | ~152 |
| a 256-entry table lookup and radix conversion | `0x6630..0x6708` | ~216 |
| CRC-32 (three call shapes sharing one 256-entry table) | `0x6708..0x67bc` | 180 |
| CRC-32 table (well-known reflected `0xEDB88320` polynomial, 256×4 bytes) | `0x67c0..0x6bc0` | 1,024 |
| radix/`itoa`-style conversion, continues past `0x7204` | `0x67c4..` (crosses the item boundary) | unresolved |

This is a **private, stage-2-only copy** of these routines. The pinned
NationalChip `lvp_kws` checkout (commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`)
tracks `utility/libc/memset.c` and prebuilt `utility/libc/csky/memset*.o`, but
no `.c` source for `strcmp`/`strchr`/`strlen`/`strnlen`/`memcpy`/CRC-32 in
this directory — `include/utility/libc/string.h` declares them but the
bodies are not in the tracked tree. The main-image occurrences of `memset`
(package `0x12f58`, `runtime_gx8002_memset.c`) and `memcpy` (package
`0x25738` region, `runtime_gx8002_memcpy.c`) are **different compiled
bodies** at different package offsets — confirmed by disassembling both and
by direct byte comparison — so they do not cover this stage-2 occurrence and
this occurrence does not retroactively cover theirs.

## What CD-005 closes

`runtime_gx8002_stage2_libc.c` is a clean-room reimplementation of
`strcmp`, `strchr`, `strlen`, and `strnlen` reviewed against the decoded
stock control flow above (not copied from retained bytes). `strlen` and
`strnlen` use plain byte loops rather than the stock's word-at-a-time
"hasless" trick or its unaligned-prefix handling; behavior is unaffected
(the returned length/pointer is identical for every input), and the smaller
code still fits its stock envelope. `strcmp` returns the sign of the first
differing byte (or of the length difference at a shared terminator) rather
than the stock's exact `-1`/`0`/`1` encoding; this matches the documented C
`strcmp` contract, which only guarantees sign. Nothing calling these
functions from elsewhere in stage 2 is known to depend on the retained
implementation detail rather than the documented C contract.

`build_gx8002_stage2_libc_candidate.py` compiles the four leaves with
`-Os -mcpu=ck804ef -mhard-float -ffreestanding -fno-builtin
-ffunction-sections -fdata-sections -Wall -Wextra -Werror` (no SDK object is
linked). Each compiles well under its stock envelope:

| Symbol | Package offset | Stock envelope | Compiled bytes |
| --- | --- | --- | --- |
| `open_cfw_gx8002_stage2_strcmp` | `0x62c0` | 36 | 24 |
| `open_cfw_gx8002_stage2_strchr` | `0x6330` | 26 | 22 |
| `open_cfw_gx8002_stage2_strlen` | `0x634c` | 74 | 16 |
| `open_cfw_gx8002_stage2_strnlen` | `0x63a0` | 40 | 22 |

`verify_gx8002_stage2_libc.py` decodes both the stock bytes (via the
objcopy/objdump technique above) and the compiled candidate (per-`.text.<symbol>`
section of the unlinked `.o`, since neither depends on its link address —
no `lrw` of an absolute literal, no call to a fixed address) with the same
restricted leaf-instruction interpreter, and checks each against an
independent Python oracle. 13,908 decoded cases cover boundary strings
(empty, all-`0x00`, all-`0xff`, embedded high bytes), four base-address
alignments per case, and `strnlen` bounds from 0 through past the string end.
`test_gx8002_stage2_libc.py` additionally compiles the source natively on
macOS and checks it against `ctypes`-driven black-box cases. This is a leaf
interpreter, not a C-SKY system emulator; it establishes decoded behavioral
equivalence for the tested inputs, not hardware or timing qualification.

Bytes closed by this item: 24 + 22 + 16 + 22 = 84 compiled-C bytes, replacing
84 of the 172 bytes across the four stock envelopes (36 + 26 + 74 + 40 = 176);
the remaining 92 bytes of those four envelopes become `generated_unreachable_fill`
(the stock tail bytes of `strlen`/`strnlen`/`strcmp`/`strchr` are no longer
reachable once the smaller candidate bodies occupy their entry points, and no
other code in this package is known to branch into their interiors).

## What remains in `0x5204..0x7204`

Roughly 8,108 bytes are still retained stock after this item:

- The diagnostic register-dump routine and device-registration helper
  (`0x5204..0x62c0`, ~3,772 bytes) — calls the printf wrapper at `0x61f4`,
  which is outside this span.
- The `strstr`/`memmem`-style search (`0x62e4..0x6330`, 76 bytes).
- The `strlen` word-trick constants (`0x6398..0x63a0`, 8 bytes — orphaned,
  no longer referenced by the replaced `strlen`, but not yet claimed).
- `memset` and `memcpy` (`0x63c8..0x652a`, 350 bytes) — a different, more
  optimized (16-byte-unrolled, alignment-masked) algorithm than the
  main-image occurrences already admitted; needs its own decoded-execution
  harness modeled on `compare_gx8002_memset.py`.
- The second bounded search, the itoa/ctype dispatch table, and the 256-entry
  radix lookup+conversion (`0x652c..0x6708`, ~324 bytes).
- CRC-32 code and its 1,024-byte table (`0x6708..0x6bc0`, 1,204 bytes) — the
  table is the well-known reflected `0xEDB88320` polynomial and is
  reproducible as `generated_source_data` (see the existing
  `gx8002-crc-recovery.md` tranche for the pattern), not copied bytes.
- A radix/`itoa`-style conversion routine starting at `0x67c4` that continues
  past this item's `0x7204` boundary into whatever item covers the next
  package span; needs coordinating with that item rather than being split
  blindly.

None of this remaining code was found to have an upstream `.c` match in the
pinned NationalChip checkout; all of it needs the same decompile-then-review
route as this item, or a positive upstream source match if one turns up
elsewhere in the SDK tree.
